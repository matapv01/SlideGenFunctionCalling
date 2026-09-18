# Chiến lược RAG cho Slidegenius

## 1. Mục tiêu và phạm vi

RAG của Slidegenius phải trả lời đúng câu hỏi dựa trên tài liệu mà người dùng
đã gắn vào cuộc trò chuyện, đồng thời cung cấp đủ ngữ cảnh để tạo slide. Mục
tiêu chính là:

- hiểu cấu trúc tài liệu trước khi truy vấn;
- lấy đúng mức thông tin: tổng quan thì lấy outline, hỏi chi tiết thì lấy
  bằng chứng chi tiết kèm nhánh cha;
- không đưa các phần không liên quan vào prompt của LLM;
- dùng chung các thành phần đã có của Slidegen: LLM, embedding local, SQLite,
  workflow tiền xử lý DOCX và workflow tạo slide;
- lưu được nguồn/citation để kiểm tra câu trả lời và lịch sử tạo slide.

Phiên bản hiện tại hỗ trợ DOCX. Các loại file khác chỉ nên thêm sau khi chúng
được chuyển về cùng một hợp đồng dữ liệu chuẩn, không tạo thêm một workflow
RAG độc lập cho từng loại file.

## 2. Nguyên tắc kiến trúc

Các nguyên tắc về phân cấp, truy vấn và provenance chỉ được áp dụng ở mức kiến
trúc; không được kéo theo runtime PostgreSQL, vector database hay LangGraph
riêng vào backend hiện tại. Biên giới của hệ thống là:

```text
DOCX
  -> DocumentPreprocessingService
  -> canonical plain_text + document_structure
  -> hierarchical chunk materializer
  -> existing local embedding provider
  -> SQLite document/chunk index
  -> LLM query planner
  -> hierarchical retrieval
  -> context + citations
  -> chatbot answer OR slide brief
  -> existing slide workflow
```

Mỗi lớp chỉ có một trách nhiệm:

| Lớp | Trách nhiệm | Không làm |
| --- | --- | --- |
| `DocumentPreprocessingService` | DOCX thành Markdown/text chuẩn và cây JSON | Không truy vấn RAG, không tự tạo citation |
| `DocumentRagService` | Materialize cây, embed, rank, mở rộng cây, đóng gói context | Không quyết định ý định người dùng bằng prompt LLM |
| `RagQueryPlanner` | Quyết định có cần RAG, viết lại query, chọn mode và budget | Không chọn trực tiếp `node_id` trong database |
| `ChatbotService` | Điều phối planner, RAG, hội thoại và slide generation | Không lặp lại logic chunking |
| SQLite repository | Lưu document, generation chunk và citation | Không chứa logic ranking |
| `SlideGenerationService` | Nhận brief/context và đi vào workflow slide hiện có | Không tự đọc DOCX lần nữa |

## 3. Tiền xử lý tài liệu là nguồn chuẩn duy nhất

Khi upload DOCX, hệ thống chạy một luồng tự động:

1. Đọc nội dung và phát hiện vùng đã có heading/cấu trúc.
2. Giữ nguyên vùng có cấu trúc.
3. Chỉ gọi LLM cho vùng không có cấu trúc để phân cấp, gom nhóm hoặc merge.
4. Xuất ra `plain_text` và `document_structure` dạng cây.
5. Lưu Markdown/canonical artifact để có thể re-index mà không cần đọc lại
   DOCX hoặc gọi LLM lần nữa.
6. Từ cây chuẩn tạo các node RAG rồi batch-embed.

Với tài liệu không có heading, LLM chỉ trả về outline nhỏ gồm `title`,
`children` và các `block_ids`. Backend giữ nguyên source block rồi tự gắn vào
cây; LLM không phải sao chép toàn bộ văn bản vào JSON. Nếu outline không hợp lệ
sau các lần retry, canonical Markdown vẫn được index dưới một root node phẳng,
không làm mất tài liệu hoặc làm hỏng luồng hỏi đáp.

RAG không được tự phân tích lại Markdown để đoán heading lần thứ hai. Nếu một
đoạn đã được workflow tiền xử lý xác định là một node, mọi lần retrieval sau
đó phải dùng đúng node và quan hệ cha/con của nó.

### 3.1 Ảnh trong DOCX và kiểm chứng bằng Qwen-VL

Ảnh không được đưa thẳng vào deck chỉ vì nó tồn tại trong DOCX. Trong lúc tạo
canonical artifact, `DocumentImageExtractor` đọc relationship của DOCX, lưu
asset private và gắn mỗi occurrence với `section_path`, heading gần nhất,
đoạn văn lân cận và thứ tự xuất hiện. Metadata này được lưu cùng
`chatbot_documents.images_json`; không tạo vector database hay service ảnh
riêng.

Trước planner, node `image_verifier` gửi ảnh cùng toàn bộ slide chunks hiện
tại cho `ImageRelevanceService`. Qwen-VL chỉ trả về quyết định có dùng hay
không, slide chính, confidence, vai trò và lý do. Các assignment được ghi vào
state để mọi planner batch thấy cùng một kết quả. Khi layout được chọn, executor
inject đúng asset đã duyệt vào image slot tương ứng và copy asset vào project.

Ảnh từ DDGS dùng cùng verifier nhưng theo candidate set: search lấy nhiều ứng
viên, Qwen so sánh ứng viên với nội dung slide và role của slot, sau đó executor
mới chọn URL được duyệt. Nếu endpoint đang chạy text-only hoặc verifier lỗi,
đây là enrichment tùy chọn: hệ thống giữ luồng ảnh hiện tại và không làm hỏng
việc tạo slide.

Nguyên tắc này tránh cả hai lỗi: lấy ảnh “cùng chủ đề” nhưng sai đối tượng, và
ép mọi ảnh trong tài liệu vào deck. Qwen được cung cấp context thực tế thay vì
rule theo tên tài liệu hay từ khóa cố định.

## 4. Mô hình index phân cấp

Mỗi chunk active có các tọa độ ổn định:

- `document_id`: tài liệu thuộc user nào;
- `node_key`: tọa độ cây, ví dụ `1`, `1.2`, `1.2.3`;
- `parent_node_key`: node cha, root có giá trị `null`;
- `level`: độ sâu trong cây;
- `node_kind`: `root_summary`, `section_summary` hoặc `content`;
- `section_path`, `title`, `content`, `embedding`.

Một node có thể có một summary chunk và một hoặc nhiều content chunk. Cách này
cho phép broad query lấy summary còn targeted query lấy bằng chứng mà không
làm phẳng cây.

### Root

Mỗi document có một `root_summary` ngắn, gồm tiêu đề, các section cấp cao,
preview nội dung cấp cao và tên các subsection. Root dùng để trả lời “tài liệu
này nói về gì?” và làm bước định hướng trước khi lấy chi tiết.

### Section summary

Node branch và các section ở level cao có `section_summary`. Summary gồm nội
dung trực tiếp đã rút gọn và danh sách subsection. Không copy toàn bộ nội dung
của descendants vào summary, tránh index phình to và tránh lặp context.

### Content detail

`content` chỉ chứa body trực tiếp của node đó, được chia theo paragraph ở giới
hạn khoảng 2.400 ký tự. Nội dung của node con không được gộp vào body của node
cha. Vì vậy retrieval có thể lấy một bằng chứng cụ thể và vẫn truy ngược được
đường dẫn cha.

## 5. LLM query planner

Planner chạy sau khi đã biết conversation có document `ready`. LLM chỉ trả về
JSON gồm:

```json
{
  "needs_rag": true,
  "mode": "deck_from_document",
  "source_policy": "document_preferred",
  "queries": ["các luận điểm chính", "số liệu quan trọng"],
  "include_root": true,
  "include_ancestors": true,
  "include_siblings": false,
  "max_detail_nodes": 8,
  "reason": "Cần dữ kiện trong tài liệu để viết deck"
}
```

LLM được phép viết query thông tin cần tìm, nhưng không được tự chọn ID của
node. Backend luôn normalize JSON, giới hạn 1–4 query, giới hạn budget và có
fallback deterministic nếu LLM lỗi hoặc trả JSON không hợp lệ.

Planner phải dùng ngôn ngữ của người dùng và phân biệt:

- chào hỏi/nói chuyện thông thường: `needs_rag=false`;
- hỏi về tài liệu, tóm tắt, phân tích, trích dẫn: `needs_rag=true`;
- “làm slide từ tài liệu”: `deck_from_document`;
- “làm slide về X” khi có tài liệu: `topic_grounded`, không mặc định lấy cả
  tài liệu;
- câu hỏi có nhiều khía cạnh hoặc so sánh: `multi_facet`, mỗi query đại diện
  cho một facet.

## 6. Các mode retrieval

| Mode | Cách lấy context | Dùng cho |
| --- | --- | --- |
| `document_overview` | Root + section cấp cao, gần như không lấy detail | “Tài liệu nói về gì?”, tóm tắt outline |
| `deck_from_document` | Root + phủ section rộng; detail theo số slide và budget | Tạo deck bao quát toàn tài liệu |
| `targeted_section` | Anchor match + parent chain + một ít child detail; sibling tùy plan | Hỏi một số liệu, đoạn hoặc section |
| `topic_grounded` | Root/outline probe trước; chỉ bung detail trong branch outline match | Tạo slide về một chủ đề cụ thể trong tài liệu |
| `multi_facet` | Mỗi facet có anchor riêng, có thể lấy sibling để so sánh | So sánh, liệt kê nhiều khía cạnh |
| `none` | Không truy vấn document | Casual chat hoặc câu hỏi chỉ dựa trên hội thoại |

### Trường hợp tạo slide từ toàn bộ document

Ví dụ: “làm deck 10 slide từ tài liệu này”. Retrieval sẽ:

1. lấy root;
2. chọn các section cấp cao theo thứ tự tài liệu để phủ đều, không chỉ chọn
   section có cosine score cao nhất;
3. dùng `target_slide_count` để ước lượng độ rộng outline;
4. lấy thêm detail từ các branch đã chọn trong giới hạn `max_detail_nodes`;
5. chuyển context và citation cho bước viết lại brief/kịch bản rồi mới vào
   workflow slide.

### Trường hợp tạo slide theo một chủ đề

Ví dụ: “làm slide về chiến lược giá theo tài liệu”. Hệ thống:

1. lấy root để biết document có đề cập chủ đề không;
2. chấm điểm section summary cấp cao;
3. chỉ khi có section đạt ngưỡng liên quan mới bung anchor/detail trong chính
   các branch đó;
4. nếu không có branch phù hợp, giữ root/outline để LLM biết tài liệu không
   đủ dữ kiện, không nhét một detail ngẫu nhiên vào slide brief.

### Trường hợp hỏi chi tiết

Với câu hỏi “doanh thu năm 2024 là bao nhiêu?” hệ thống ưu tiên content node
khớp nhất, kèm section summary/ancestor để giữ nghĩa. Child detail chỉ được
thêm trong budget; sibling chỉ thêm khi planner xác định cần so sánh hoặc xem
toàn bộ danh sách.

## 7. Ranking và đóng gói context

Retrieval hiện tại dùng chiến lược nhẹ, phù hợp với SQLite và embedding local:

1. Chuẩn hóa và loại query trùng.
2. Tách một số facet từ các query có “và/and” hoặc dấu phân cách.
3. Batch-embed các query variant trong một lần gọi.
4. Chấm điểm mỗi chunk bằng cosine similarity, cộng lexical bonus nhỏ cho
   title/section/content và ưu tiên nhẹ cho summary node ở broad query.
5. Gom điểm theo node, giữ một anchor cho mỗi facet trước khi fill bằng global
   score.
6. Mở rộng theo cây: ancestor, child, sibling theo plan.
7. Dedupe theo chunk ID và content fingerprint.
8. Dừng khi context đạt giới hạn 14.000 ký tự.

`max_detail_nodes` là hard budget cho tổng số anchor và child detail. Root,
section summary, ancestor và sibling summary không tiêu tốn budget này. Nhờ đó
planner không thể vô tình làm context phình ra chỉ vì chọn nhiều facet.

Mỗi source được đóng gói cùng:

```text
[Source N | level L | node_kind | section: A / B]
evidence...
```

Citation lưu `document_id`, `chunk_id`, section, title, level, node key, parent,
node kind, role và similarity. Answer LLM được yêu cầu dùng `[Source N]` khi
khẳng định dựa trên tài liệu và nói rõ khi tài liệu không có thông tin.

## 8. Tích hợp với chatbot và slide generation

Luồng chatbot thống nhất là:

```text
user message
  -> contextualize theo memory
  -> planner quyết định RAG
  -> retrieve theo mode/budget
  -> trả lời chat bình thường
```

Khi message là yêu cầu tạo slide:

```text
user brief + answers làm rõ + target_slide_count
  -> planner/RAG
  -> viết lại kịch bản/brief dựa trên retrieved context
  -> SlideGenerationService
  -> workflow slide hiện có
  -> project + citation + metadata được lưu vào conversation
```

Không chia lại thành workflow `idea`, `doc có heading`, `doc không heading`
cho chatbot. Các nhánh đó chỉ là chi tiết bên trong tiền xử lý canonical; ở
tầng chatbot chỉ còn một hành động “generate slide”. Manual workflow là mode
riêng và không được trộn vào RAG chatbot.

## 9. Lưu trữ, migration và dữ liệu cũ

Document và chunk đều bị scope theo `user_id` và `session_id`; không được lấy
chunk chỉ bằng một ID không kiểm tra ownership.

Chunk index dùng generation an toàn:

- document giữ `chunk_index_version` active;
- chunk mới được lưu với ordinal thuộc generation mới;
- query chỉ đọc generation active;
- chunk cũ không bị xóa ngay vì citation lịch sử còn tham chiếu đến chúng;
- document cũ từ flat schema được lazy-backfill từ canonical Markdown/JSON khi
  retrieval đầu tiên nhìn thấy row chưa có `node_key`;
- backfill thành công đổi active generation atomically; lỗi tạm thời giữ index
  cũ để chatbot vẫn trả lời được và sẽ retry ở request sau.

Khi đổi embedding model, cần re-index toàn bộ document. Không được trộn vector
của hai model trong cùng active generation. Đây là một điểm cần bổ sung thêm
metadata fingerprint của embedding model nếu hệ thống bắt đầu thay model thường
xuyên.

## 10. Các giới hạn đang dùng

| Config | Giá trị hiện tại | Ý nghĩa |
| --- | ---: | --- |
| `CHATBOT_RAG_TOP_K` | 6 | Số anchor tối đa trước khi fill |
| `CHATBOT_RAG_MAX_CONTEXT_CHARS` | 14.000 | Trần context gửi cho LLM |
| `CHATBOT_RAG_MIN_SIMILARITY` | 0,28 | Ngưỡng detail/outline liên quan |
| `CHATBOT_RAG_CHUNK_CHARS` | 2.400 | Kích thước content chunk |
| `CHATBOT_RAG_MAX_ANCESTOR_DEPTH` | 4 | Số level cha tối đa |
| `CHATBOT_RAG_MAX_SIBLINGS` | 3 | Số sibling summary tối đa mỗi anchor |
| `CHATBOT_RAG_OVERVIEW_SECTION_LIMIT` | 24 | Số section outline tối đa |
| `CHATBOT_RAG_DETAIL_NODE_LIMIT` | 8 | Detail budget mặc định của service |
| embedding batch | 32 | Số text embed mỗi batch |

Các giới hạn này phải được thay đổi ở config, không hard-code thêm trong router
hoặc frontend. `target_slide_count` chỉ điều chỉnh độ phủ section của
`deck_from_document`; nó không được vượt plan limit của subscription.

## 11. Đánh giá chất lượng và kiểm thử

Mỗi thay đổi RAG cần giữ các nhóm test sau:

- materialize đúng root, level, `node_key`, parent và node kind;
- document có heading, document có heading lồng nhau và document không heading;
- overview lấy root/high-level trước detail;
- targeted giữ anchor trong parent chain;
- topic không bung detail của branch không liên quan;
- multi-facet không để một facet chiếm toàn bộ anchor;
- hard detail budget không bị vượt bởi child expansion;
- citation vẫn trỏ đến chunk thật;
- user/session khác nhau không nhìn thấy document của nhau;
- LLM planner trả JSON lỗi vẫn có fallback query an toàn;
- index cũ được backfill mà citation cũ không bị hỏng;
- đang tạo slide vẫn chat được, nhưng không khởi động deck thứ hai.

Các kiểm tra tối thiểu trước khi deploy:

```bash
python3 -m compileall -q backend
docker compose build slidegen
docker compose run --rm slidegen pytest -q backend/tests
docker compose up -d --no-deps slidegen
```

## 12. Đánh giá hiện tại và hướng tối ưu tiếp theo

Hiện tại kiến trúc đã sạch theo đúng boundary: một preprocessing service, một
RAG service, một planner, repository SQLite dùng chung và không có runtime RAG
thứ hai. Retrieval đã batch-embed query, lưu vector lâu dài, lọc theo session,
dedupe context, giới hạn context và backfill dữ liệu cũ an toàn.

Các tối ưu tiếp theo chỉ cần khi quy mô tài liệu tăng:

1. lưu `embedding_model`/dimension fingerprint trên document và tự đánh dấu
   re-index khi model đổi;
2. thêm cache embedding cho query ngắn trong một session nếu latency thực tế
   yêu cầu;
3. khi số chunk rất lớn, thay linear scan bằng vector index được quản lý trong
   infrastructure nhưng vẫn giữ repository/application port hiện tại;
4. thêm metrics: số chunk đọc, top score, số source sau dedupe, context chars,
   thời gian embed/retrieve và tỷ lệ planner fallback;
5. bổ sung job dọn generation cũ không còn citation sau khi có retention policy
   rõ ràng;
6. thêm reranker chỉ khi benchmark chứng minh cosine + lexical chưa đủ tốt.

Không nên tối ưu bằng cách bỏ root/ancestor, bỏ citation, đưa LLM vào vòng lặp
cho từng chunk, hoặc tạo thêm database riêng. Những cách đó có thể giảm một
phần latency nhưng làm mất tính giải thích, tăng chi phí và phá vỡ cấu trúc
hiện tại.
