# Kế hoạch training GRPO cho SlideGen

## 1. Mục tiêu

Mục tiêu của hệ thống training là tối ưu trực tiếp policy tạo slide XML bằng
GRPO, bắt đầu từ base model instruction và LoRA mới, không qua giai đoạn SDFT.

Policy được huấn luyện để:

- Trả về đúng một XML tool call có cấu trúc hợp lệ.
- Chỉ gọi layout đã được pipeline production phân công.
- Bảo toàn nội dung và ngôn ngữ của slide nguồn.
- Tạo slide không tràn chữ, không va chạm textbox và có bố cục hợp lý.
- Tuân thủ deck style chung của toàn bộ presentation.
- Hoạt động tương thích với pipeline SlideGen song song ở backend.
- Có thể resume đầy đủ sau khi job H100 bị ngắt.

Trong lúc train, policy, retrieval, render và reward chạy local; không gọi
planner API. Riêng bước rebuild corpus trước khi train có thể gọi planner/VLM
qua endpoint trong `backend/config.py`, với credential provider ở `.env`.

## 2. Phạm vi đã triển khai

Luồng đã được triển khai trong các file chính:

| Thành phần | File |
|---|---|
| Entrypoint và orchestration training | rl/train.py |
| GRPO trainer và DAPO accumulation scaling | rl/grpo_trainer.py |
| Prompt, tool schema và batch renderer | rl/slidegen_adapter.py |
| Composite reward | rl/rewards/composite_reward.py |
| ViT aesthetic reward | rl/rewards/aesthetic_reward.py |
| XML overflow/collision checks | BE renderer/analyzer; điểm phạt được tính trong `rl/rewards/composite_reward.py` |
| Offline corpus loader | scripts/generate_challenge_dataset.py |
| Regression tests | rl/test_grpo_pipeline.py |

Các thành phần SDFT cũ đã bị loại khỏi luồng training. Entrypoint hiện tại luôn
train trực tiếp GRPO với LoRA.

## 3. Kiến trúc tổng thể

Luồng dữ liệu và cập nhật policy:

    Offline corpus
        |
        v
    Group theo document
        |
        +--> Train documents
        |
        +--> Held-out evaluation documents
        |
        v
    Production-compatible layout assignment
        |
        v
    Prompt + một assigned XML tool
        |
        v
    Base model + trainable LoRA
        |
        v
    N completions cho cùng một prompt
        |
        v
    Parse -> validate -> apply deck style -> execute XML
        |
        +--> content rewards
        +--> semantic reward
        +--> XML overflow/collision reward
        +--> parallel Chromium render
        +--> batched ViT aesthetic reward
        |
        v
    Group-relative advantages
        |
        +--> standard group-relative advantages (zero-variance groups stay zero)
        |
        v
    DAPO loss -> optimizer update -> checkpoint/evaluation

Một GRPOTrainer duy nhất được sử dụng cho toàn bộ run. Trainer không bị tạo lại
sau mỗi optimizer step, vì vậy Adam moments, learning-rate scheduler, RNG state
và dataloader state không bị reset.

## 4. Kế hoạch dữ liệu

### 4.1. Nguồn dữ liệu

Corpus mặc định của `rl/train.py`:

    rl/data/grpo_replanned_dataset.json

`scripts/rebuild_grpo_corpus.py` lấy nội dung nguồn từ
`rl/data/sft_function_call_dataset.json` để dựng corpus trên qua pipeline BE.
GRPO dùng nội dung nguồn, plan/style mới và ảnh đã duyệt để tạo bài toán rollout.
Ground-truth tool call cũ không được dùng làm target supervised.

Số liệu tham chiếu từ corpus nguồn (không xác nhận corpus rebuilt đã được tạo):

- 49 documents.
- 414 slides.
- 44 documents cho train.
- 5 documents held-out cho evaluation.
- 372 train prompts.
- 42 evaluation prompts.

Các con số trên phụ thuộc corpus hiện tại và GRPO_EVAL_DOCS=5.

### 4.2. Split chống leakage

Split được thực hiện ở cấp document, không phải cấp slide.

Quy trình:

1. Group toàn bộ rows bằng doc_id.
2. Shuffle danh sách document bằng GRPO_DATA_SEED.
3. Lấy GRPO_EVAL_DOCS document đầu tiên làm evaluation.
4. Toàn bộ slide còn lại thuộc train.

Do đó các slide trong cùng một presentation không thể xuất hiện đồng thời ở
train và evaluation.

### 4.3. Tính tái lập

Các nguồn randomness chính được khóa bởi GRPO_DATA_SEED, mặc định là 42:

- Thứ tự document.
- Train/eval split.
- Dataset sampling của Trainer.
- Generation seed của Transformers/TRL.

Dataset prompt sau khi chuẩn bị được snapshot vào:

    GRPO_OUTPUT_DIR/dataset_snapshots/train.json
    GRPO_OUTPUT_DIR/dataset_snapshots/eval.json

Snapshot cho phép audit chính xác prompt, assigned tool, deck style và nội dung
đã đi vào một run.

## 5. Đồng bộ với pipeline production

### 5.1. Tool source

RL sử dụng trực tiếp XML TOOLS_DICT của backend. Không duy trì một bản schema
tool riêng, nhờ đó thay đổi schema production sẽ được phản ánh vào training.

### 5.2. Image mode

Corpus GRPO mới được dựng từ nội dung slide trong JSON hiện có; category,
design instruction, ảnh và tool call cũ không được dùng làm nhãn. Chạy:

    uv run --locked python scripts/rebuild_grpo_corpus.py --max-docs 1 --max-slides 2 --output /tmp/grpo_replanned_smoke.json
    uv run --locked python scripts/rebuild_grpo_corpus.py

Tìm ảnh bên ngoài bật mặc định. Dùng `--no-allow-external-search` để chủ động
không tìm ảnh; cờ `--allow-external-search` cũ vẫn dùng được. Manifest kiểm tra
chế độ tìm ảnh: dùng output mới khi đổi chế độ, hoặc giữ chế độ cũ để resume.

Planner/VLM model names và base URLs được đặt trong `backend/config.py`; `.env`
chỉ chứa API credentials. Builder gọi lại production deck style planner, slide
planner, image search và
Qwen-VL verifier. Chỉ ảnh được duyệt mới được tải vào `static/output/grpo_image_cache/`;
phase-two planner nhận visual notes/caption từ VL để tạo final content và layout
brief. Kết quả được ghi thành `rl/data/grpo_replanned_dataset.json` và có thể
resume theo document sau khi gián đoạn. Qwen3-8B là text-only; nó không thể làm
vision verifier.

Khi train, assign_layouts dùng cùng RAG retrieval production nhưng query gồm
retrieval query, topic, final content, layout brief và mô tả ảnh đã duyệt. Tool
được chọn trước mỗi rollout; Qwen3-8B sinh function call trong rollout để GRPO
tối ưu. Ảnh thiếu hoặc không đạt ngưỡng confidence chuyển slide sang no-image.
Loader chỉ chấp nhận ảnh rebuilt có file local dưới static/output và confidence
>= 0.5.

### 5.3. Deck-wide layout assignment

RL gọi assign_layouts của section batch orchestrator trong backend.

Layout assignment có các đặc tính:

- Dùng local SentenceTransformer và FAISS để retrieve layout liên quan.
- Áp dụng đúng image-mode filter.
- Hạn chế lặp layout liền kề.
- Cân bằng usage trong cùng deck.
- Gán preferred_tool_name trước khi generation song song.

Mỗi training sample chỉ nhận đúng một tool schema: tool đã được production
scheduler phân công. Policy tập trung học argument generation thay vì học lại
một quyết định layout vốn đã thuộc trách nhiệm của scheduler.

Dry-run toàn corpus đã phủ đủ 13 trên 13 layout no-image khả dụng.

### 5.4. Deck style

Mỗi document nhận một DeckStylePlan bất biến. Bốn palette deterministic được
phân bổ theo source document ID để tăng độ đa dạng mà vẫn tái lập được.

Deck style xuất hiện trong prompt và được apply lại trước khi reward execute XML
bằng apply_deck_style_to_tool_call, giống production. Vì vậy reward đánh giá
slide sau production transform, không đánh giá một trạng thái mà inference
không bao giờ sử dụng.

### 5.5. Prompt contract

System prompt tái sử dụng:

- Math/equation rules.
- XML content rules.
- Tool/schema constraints.
- RL serialization contract.

Human prompt tái sử dụng các trường production:

- Slide context.
- Deck style contract.
- Slide topic.
- Presentation direction.
- Image mode.
- Visual layout request.
- Approved images.
- Assigned layout.
- Slide plan.
- Design brief.
- Slide index và deck length.
- Source content.
- Previous attempt/evaluation placeholders.

Khác biệt duy nhất có chủ đích là transport. Production dùng native tool call,
còn raw GRPO completion được serialize thành:

    <tool_call>{"name":"...","arguments":{...}}</tool_call>

Reward bắt buộc completion chỉ chứa đúng một serialized tool call.

## 6. Model và LoRA

### 6.1. Base model

Mặc định TRAINING_MODEL_ID là Qwen/Qwen3-8B. Trên H100 có thể trỏ biến này tới
local path của đúng checkpoint Qwen3-8B.

Training dùng chat template gốc trong tokenizer và truyền enable_thinking=False,
đồng thời giữ hợp đồng tool-call JSON mà Qwen3 template hỗ trợ.

Base model không được hard-code vào checkpoint RL. Khi resume, Trainer load lại
base model rồi nạp LoRA và state từ checkpoint.

### 6.2. LoRA configuration

Cấu hình hiện tại:

| Tham số | Giá trị |
|---|---:|
| Rank | 16 |
| Alpha | 32 |
| Dropout | 0 |
| Bias | none |
| Task type | Causal LM |

Target modules:

- q_proj
- k_proj
- v_proj
- o_proj
- gate_proj
- up_proj
- down_proj

Entrypoint bắt buộc USE_LORA=true. Full-model fine-tuning bị chặn để checkpoint
nhỏ hơn, resume an toàn hơn và phù hợp với tài nguyên H100 mục tiêu.

### 6.3. Precision và memory

- CUDA có BF16 support: dùng bfloat16.
- CUDA không có BF16: dùng float16.
- CPU fallback: dùng float32.
- TF32 được bật trên CUDA.
- Gradient checkpointing được bật mặc định.
- model.config.use_cache được tắt khi train.
- PyTorch allocator dùng expandable segments để giảm fragmentation.

Nếu TRAINING_GPU không được đặt, script chọn GPU có lượng VRAM trống lớn nhất.

## 7. Cấu hình GRPO/DAPO

Cấu hình mặc định:

| Tham số | Giá trị |
|---|---:|
| TOTAL_STEPS | 500 |
| LEARNING_RATE | 1e-6 |
| PER_DEVICE_TRAIN_BATCH_SIZE | 1 |
| GRADIENT_ACCUMULATION_STEPS | 16 |
| NUM_GENERATIONS | 4 |
| GRPO_GENERATION_BATCH_SIZE | 4 completions mỗi generation window |
| MAX_COMPLETION_LENGTH | 3072 |
| GRPO_TEMPERATURE | 0.7 |
| GRPO_TOP_P | 0.8 |
| GRPO_TOP_K | 20 |
| GRPO_BETA | 0.0 |
| GRPO_EPSILON | 0.2 |
| GRPO_EPSILON_HIGH | 0.28 |
| GRPO_LOSS_TYPE | dapo |
| scale_rewards | group |

Audit bằng tokenizer của Qwen3 trên 414 `tool_call` tham chiếu trong corpus nguồn:
p50=289, p90=849, p95=1.136, p99=1.706, max=2.419 token sau khi bọc đúng
`<tool_call>…</tool_call>`. Giới hạn 512 sẽ cắt 92/414 (22,2%) mẫu tham chiếu;
3.072 bao phủ giá trị lớn nhất và thêm khoảng đệm. Prompt dài nhất đã chuẩn bị là
4.389 token, nên prompt cộng completion cap bằng 7.461/40.960 token context.
Đây là phép đo trên tool call tham chiếu, không dự đoán chắc chắn độ dài rollout;
pilot vẫn phải theo dõi `completions/clipped_ratio`.
| mask_truncated_completions | true |

### 7.1. Ý nghĩa batch configuration

Với một process GPU và per-device batch bằng 1:

- `GRPO_GENERATION_BATCH_SIZE=4` là tổng bốn completions trong một generation
  window; sampler lặp cùng một prompt `NUM_GENERATIONS=4` lần.
- `steps_per_generation=4`; bốn completions của prompt đó được chia thành bốn
  micro-step, mỗi micro-step xử lý một completion.
- `gradient_accumulation_steps=16` gom bốn generation windows (bốn prompt groups)
  vào một optimizer update, tương đương 16 completions.
- TRL tính DAPO token normalizer theo tổng completion tokens của một generation
  window. Trainer chia từng micro-step loss cho
  `gradient_accumulation_steps / steps_per_generation` (mặc định bằng 4), để
  optimizer update đầy đủ lấy trung bình qua bốn windows.
- Nếu epoch kết thúc bằng một optimizer update ngắn hơn, trainer dùng số micro-step
  thực tế của update cuối, nhưng chỉ khi số đó vẫn là bội của `steps_per_generation`.
- Trainer từ chối cấu hình accumulation không chia hết cho `steps_per_generation`
  và dừng nếu optimizer update thực tế bị cắt giữa generation window.

### 7.2. DAPO controls

DAPO được chọn để dùng asymmetric clipping:

- epsilon = 0.2 cho clip thấp.
- epsilon_high = 0.28 cho clip cao.
- Truncated completions bị mask khỏi loss.
- beta = 0 nên không thêm KL penalty/reference model mặc định.

Mục tiêu là cho phép update tích cực hơn với action tốt, trong khi vẫn giới hạn
policy drift và không tốn VRAM cho một reference model riêng.

## 8. Composite reward

### 8.1. Quy tắc validity trước tiên

Một completion bị coi là invalid nếu:

- Không parse được tool call.
- Tool name khác assigned_tool_name.
- arguments không thỏa schema.
- XML tool execution thất bại.

Invalid completion nhận:

    reward = RL_INVALID_REWARD = -2.0

Invalid completion không được render và không được đưa qua ViT.

### 8.2. Reward cho completion hợp lệ

Validity và canonical format là hard gate: completion lỗi nhận riêng
`RL_INVALID_REWARD=-2.0`, không render. Với completion hợp lệ, mỗi tín hiệu reward
nằm trong `[0,1]` và chỉ xuất hiện một lần trong tổng có trọng số:

    R = w_lexical * lexical
      + w_semantic * semantic
      + w_numeric_fact * numeric_fact
      + w_dom * dom
      + w_aesthetic * aesthetic
      + w_image_loaded * image_loaded

Giá trị mặc định:

    R = 0.7 * lexical
      + 0.8 * semantic
      + 1.5 * numeric_fact
      + 0.8 * dom
      + 1.0 * aesthetic
      + 0.4 * image_loaded

| Thành phần | Range | Ý nghĩa |
|---|---:|---|
| lexical | 0 đến 1 | Tỷ lệ keyword nguồn xuất hiện trong text thực sự được frontend render, có điều chỉnh theo độ dài |
| semantic | 0 đến 1 | Mức tương đồng ngữ nghĩa đa ngôn ngữ trên toàn bộ nội dung đã chia chunk |
| numeric_fact | 0 đến 1 | Tỷ lệ số liệu được giữ nguyên và gắn với ngữ cảnh/chỉ tiêu gần đúng |
| dom | 0 đến 1 | Điểm layout chuẩn hóa từ overflow, boundary và textbox collision |
| aesthetic | 0 đến 1 | Điểm thẩm mỹ từ ViT 5 nhãn đã train |
| image_loaded | 0 đến 1 | Tỷ lệ ảnh được yêu cầu và tải đúng URL trong preview; bằng 1 nếu sample không yêu cầu ảnh |

Canonical format/tool/schema là cổng validity, không phải component hằng số được
cộng thêm vào mọi valid completion. Numeric literal được loại khỏi lexical token overlap và được mask khỏi semantic
embedding; vì vậy việc giữ số chỉ thuộc `numeric_fact`. Không còn penalty shaping
trừ lần hai sau tổng reward. Thiếu số liệu chỉ tác động
`numeric_fact`; layout chỉ tác động `dom`; ảnh lỗi chỉ tác động `image_loaded`;
thiếu nội dung được biểu diễn bởi lexical và semantic. Các tín hiệu nội dung vẫn
có thể tương quan. ViT 5 nhãn là checkpoint đã train; “chưa hiệu chuẩn” chỉ nói
về các hệ số ghép component hiện đặt thủ công, không phải ViT. Các hệ số này chưa
được fit trên preference pairwise có nhãn. Cần đánh giá phân phối, pairwise ranking
và ablation trên tập held-out trước khi chạy dài trên H100.

Semantic reward chia cả source content và text thực sự render trên frontend thành
các chunk theo tokenizer của embedder. Điểm là harmonic mean giữa source coverage
và generated-text precision: phần nội dung phía sau context limit vẫn được xét,
đồng thời text không có căn cứ trong source làm giảm precision.

Weights có thể override bằng:

- RL_REWARD_LEXICAL_WEIGHT
- RL_REWARD_SEMANTIC_WEIGHT
- RL_REWARD_NUMERIC_FACT_WEIGHT
- RL_REWARD_DOM_WEIGHT
- RL_REWARD_AESTHETIC_WEIGHT
- RL_REWARD_IMAGE_LOADED_WEIGHT

### 8.3. Content preservation

Lexical score:

1. Lowercase và tokenize từ, gồm cả số và từ một ký tự.
2. Loại một tập stopword tiếng Việt phổ biến.
3. Tính tỷ lệ keyword nguồn xuất hiện trong text thực tế do frontend render.
4. Điều chỉnh theo độ dài; lượng text dưới 30% source không thể đạt điểm lexical cao.

Semantic score:

1. Trích text từ textbox, chart accessibility labels và math labels sau khi frontend render.
2. Encode source và generated text bằng multilingual MiniLM.
3. Normalize embeddings.
4. Chia text quá dài thành chunk không mất phần cuối; dùng harmonic mean giữa source coverage và generated-text precision.

SentenceTransformer được chia sẻ với tool retriever, tránh load hai model giống
nhau trong cùng process. Lexical và semantic là hai tín hiệu khác nhau nhưng có
thể tương quan; không xem đây là hai đánh giá độc lập tuyệt đối.

### 8.4. Numeric-fact heuristic

Source number/context records được trích một lần khi chuẩn bị sample. Runtime
đối chiếu số literal theo mệnh đề (dấu câu/liên từ), bỏ qua số thứ tự bullet,
và dùng cue tăng/giảm cùng từ ngữ lân cận để phát hiện một số trường hợp gán sai.
Điểm số được đưa vào `numeric_fact` đúng một lần.

Đây là heuristic cục bộ, không phải kiểm chứng entailment tổng quát. Nó có thể
bỏ sót phủ định phức tạp, đảo quan hệ nhân quả, quy đổi đơn vị và số viết bằng
chữ. `reward_component/numeric_fact` là metric cần audit cùng ví dụ được gán
nhãn; unit test chỉ xác nhận invariant của heuristic, không chứng minh độ chính
xác trên corpus.

### 8.5. XML overflow và collision

XML được execute đúng một lần. DOM reward kiểm tra:

- Text width overflow.
- Text height overflow.
- Vượt max lines.
- Ra ngoài slide boundary.
- Va chạm giữa vùng chữ/công thức thực sự render; bỏ qua phần khung textbox
  được FE nới rộng nếu nội dung không chồng nhau.

DOM penalty weights là mức vi phạm tương đối (`text_width=0.20`,
`text_height=0.25`, `max_lines=0.20`, `slide_boundary=0.40`,
`bbox_collision=0.25`). Các issue trùng `(type, textbox, other)` chỉ tính một lần;
tổng bị cap tại 2.0 rồi đổi sang score `[0,1]` theo `1 - min(2, penalty)/2`.
`image_load` bị loại khỏi DOM vì đã có component `image_loaded` riêng.

### 8.6. Parallel rendering

Các XML hợp lệ trong rollout được render bằng:

- Một Chromium process cho cả batch.
- Nhiều page chạy đồng thời.
- Concurrency mặc định bằng RL_REWARD_RENDER_WORKERS=4.
- Dùng cùng `BROWSER_PREVIEW_URL`, viewport và device scale factor với BE production.
- Chờ image elements load/error trước screenshot và ghi reward image_loaded.
- Temporary images tự động bị xóa sau khi chấm.

Cách này tránh khởi động một browser process cho từng completion.

### 8.7. ViT aesthetic reward

ViT-small 5-label được load từ checkpoint local. Loader RL:

- Không tải pretrained base model từ Hub.
- Mở inner model_state_dict của checkpoint.
- Dựng đúng kiến trúc ViT-small.
- Load toàn bộ tensor bằng strict=True.
- Chạy eval mode.
- Chấm toàn bộ rendered images trong một tensor batch.

Năm nhãn là:

- Màu nền.
- Màu chữ.
- Size chữ.
- Bố cục.
- Tràn nội dung.

Checkpoint phải khai báo `label_semantics=1=error,0=no_error` và đúng thứ tự năm
criteria. Reward là `1 - mean(sigmoid(logits))`, tức điểm slide sạch thay vì
xác suất lỗi.

Checkpoint mặc định:

    ViT/experiments/vit_multilabel_small/best.pt

Có thể override bằng REWARD_MODEL_PATH.

## 9. Reward group không có phương sai

Không có historical EMA advantage fallback. Nếu completions trong một prompt
nhận cùng reward, GRPO giữ advantage group-relative bằng 0. Model không nhận
gradient chéo prompt/layout chỉ vì prompt đó có reward thấp hơn trung bình lịch
sử. `frac_reward_zero_std` của TRL theo dõi tần suất các nhóm như vậy; cần cải
thiện reward signal nếu tỷ lệ này cao.

## 10. Evaluation plan

Evaluation dùng document held-out và chạy cùng generation/reward pipeline với
train nhưng không cập nhật model.

Default:

- GRPO_EVAL_DOCS=5.
- GRPO_EVAL_STEPS=50.
- NUM_GENERATIONS_EVAL bằng NUM_GENERATIONS.
- Per-device eval batch bằng số generations.

Evaluation có render và ViT nên tốn thời gian đáng kể. Có thể đặt
GRPO_EVAL_STEPS=0 để tắt trong smoke test rất ngắn, nhưng không nên tắt trong
full run.

Các dấu hiệu cần theo dõi:

- Train reward tăng nhưng eval reward giảm: có nguy cơ overfit.
- Eval invalid rate không giảm: policy chưa học được schema/tool contract.
- Eval completion length thường xuyên chạm cap 3.072 hoặc `completions/clipped_ratio` tăng: output bị truncate.
- DOM reward giảm trong khi aesthetics tăng: model đang đánh đổi readability.
- `frac_reward_zero_std` cao: reward thiếu độ phân giải hoặc generations chưa đa dạng.

## 11. Checkpoint và resume

### 11.1. Checkpoint hợp lệ

Checkpoint chỉ được resume nếu chứa đầy đủ:

- adapter_model.safetensors hoặc adapter_model.bin, hoặc model weights.
- optimizer.pt.
- scheduler.pt.
- trainer_state.json.
- `rl_checkpoint_metadata.json` khớp model ID, loss type và DAPO accumulation factor hiện tại.

Legacy adapter-only checkpoint bị bỏ qua có chủ đích.

### 11.2. State được bảo toàn

Resume giữ lại:

- LoRA weights.
- Adam moments.
- Learning-rate scheduler.
- Global step.
- Trainer state.
- RNG state do Trainer quản lý.

Checkpoint interval mặc định là 25 steps và chỉ giữ ba checkpoint gần nhất.
Final adapter được lưu tại:

    GRPO_OUTPUT_DIR/final_adapter

## 12. Preflight

GRPO_PREFLIGHT mặc định bật. Trước khi tải base model và bắt đầu training,
preflight kiểm tra:

- ViT checkpoint tồn tại, load strict thành công và trả aesthetic score hữu hạn
  trên ảnh screenshot.
- REWARD_MODEL_DEVICE hợp lệ.
- Chromium executable tồn tại nếu được cấu hình.
- Playwright truy cập được `BROWSER_PREVIEW_URL`, gửi XML sample và nhận screenshot
  từ frontend XML preview.

Tool retriever mặc định fail-fast. Chỉ khi GRPO_ALLOW_RETRIEVER_FALLBACK=true,
training mới fallback về thứ tự tool trong category.

Fail-fast ngăn lỗi hạ tầng bị biến thành reward âm và làm policy học từ tín hiệu
sai.

## 13. Logging và artifacts

Mỗi run tạo:

    rl/log/grpo/run_YYYYMMDD_HHMMSS/

Các artifact chính:

- run.log: stdout/stderr đầy đủ.
- manifest.json: model, GPU, git revision, dataset và hyperparameters.
- metrics.json: Trainer log history.
- metrics_trend.png: biểu đồ loss/reward/eval/learning-rate.
- run_summary.png: tóm tắt cuối run.

Runtime metadata còn ghi CUDA visible devices, GPU snapshot, Python, Torch và
commit hiện tại để có thể truy vết experiment.

## 14. Kế hoạch chạy trên H100

### Giai đoạn 0: chuẩn bị host

Bắt buộc:

- Base model local hoặc có thể resolve từ TRAINING_MODEL_ID.
- ViT checkpoint local hoặc REWARD_MODEL_PATH hợp lệ. File
  `ViT/experiments/vit_multilabel_small/best.pt` hiện là tài sản local, không nằm
  trong Git; phải chép file này lên H100 hoặc đặt `REWARD_MODEL_PATH` tới bản đã
  chép.
- Chromium/Playwright hoạt động và `BROWSER_PREVIEW_URL` trỏ đúng route XML preview
  đang chạy trên host.
- Dataset offline tồn tại.
- Planner endpoint và Qwen-VL endpoint sẵn sàng. Chạy corpus rebuild từ nội
  dung JSON; lệnh smoke dùng hai slide, lệnh kế tiếp xử lý toàn corpus:

      uv run --locked python scripts/rebuild_grpo_corpus.py --max-docs 1 --max-slides 2 --output /tmp/grpo_replanned_smoke.json
      uv run --locked python scripts/rebuild_grpo_corpus.py

  Chép `rl/data/grpo_replanned_dataset.json` và
  `static/output/grpo_image_cache/` sang H100; đặt `GRPO_OFFLINE_DATASET`
  tới corpus mới. `TRAINING_MODEL_ID=Qwen/Qwen3-8B` chỉ sinh function call,
  không làm vision verifier.
- Đủ disk cho model, FAISS cache, checkpoints và logs.

Ví dụ:

    export TRAINING_MODEL_ID=/models/Qwen3-8B
    export REWARD_MODEL_PATH=/models/slidegen-vit-small/best.pt
    # Configure BROWSER_PREVIEW_URL in backend/config.py, not .env.
    export GRPO_OUTPUT_DIR=/data/checkpoints/slidegen-grpo
    export GRPO_FAISS_INDEX_PATH=/data/checkpoints/slidegen-grpo/tool_retriever_index
    export GRPO_REQUIRE_IMAGE_ASSETS=true

### Giai đoạn 1: infrastructure smoke test

Mục tiêu là kiểm tra startup, không đánh giá learning:

    GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-./qwen3_8b_slidegen_grpo}/smoke_1" \
    TOTAL_STEPS=1 \
    GRPO_SAVE_STEPS=1 \
    GRPO_EVAL_STEPS=0 \
    GRPO_RESUME=false \
    uv run --locked python rl/train.py

Sau đó kiểm tra checkpoint được nạp với cùng cấu hình; run phải thoát ở
`global_step=1` mà không báo lỗi:

    GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-./qwen3_8b_slidegen_grpo}/smoke_1" \
    TOTAL_STEPS=1 \
    GRPO_SAVE_STEPS=1 \
    GRPO_EVAL_STEPS=0 \
    GRPO_RESUME=true \
    uv run --locked python rl/train.py

Pass criteria:

- Preflight thành công.
- Model và LoRA load thành công.
- FAISS index load hoặc build thành công.
- Có ít nhất một generation group.
- Composite reward trả được số hữu hạn.
- Backward và optimizer step thành công.
- checkpoint-1 đủ state và resume được.

### Giai đoạn 2: pilot 10 steps

    GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-./qwen3_8b_slidegen_grpo}/pilot_10" \
    TOTAL_STEPS=10 \
    GRPO_SAVE_STEPS=5 \
    GRPO_EVAL_STEPS=5 \
    GRPO_RESUME=false \
    uv run --locked python rl/train.py

Pass criteria:

- Không OOM hoặc CUDA illegal memory access.
- Không có NaN/Inf ở loss, reward và grad norm.
- Không phải toàn bộ completion nhận -2.
- Tỷ lệ exact tool-call tăng hoặc ổn định.
- Completion length không thường xuyên chạm cap 3.072; `completions/clipped_ratio` thấp.
- Eval reward không sụt liên tục.
- Resume từ checkpoint-5 hoặc checkpoint-10 thành công.

### Giai đoạn 3: calibration 50 steps

    GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-./qwen3_8b_slidegen_grpo}/calibration_50" \
    TOTAL_STEPS=50 \
    GRPO_SAVE_STEPS=10 \
    GRPO_EVAL_STEPS=10 \
    GRPO_RESUME=false \
    uv run --locked python rl/train.py

Mục tiêu:

- Quan sát phân phối từng reward dimension.
- Xác nhận learning rate 1e-6 không quá mạnh.
- Kiểm tra train/eval gap.
- Theo dõi `frac_reward_zero_std` và metric riêng của từng reward component.
- Chọn lại reward weights nếu một dimension thống trị.

Chỉ chuyển sang full run nếu eval reward và invalid rate cải thiện.

### Giai đoạn 4: full run 500 steps

    GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-./qwen3_8b_slidegen_grpo}/full_500_run01" \
    TOTAL_STEPS=500 \
    GRPO_SAVE_STEPS=25 \
    GRPO_EVAL_STEPS=50 \
    GRPO_RESUME=false \
    uv run --locked python rl/train.py

Full run bắt đầu trong output directory riêng để dùng scheduler mới cho 500
steps, không nạp optimizer/scheduler đã kết thúc từ calibration 50 steps. Khi job
full run bị preempt, chạy lại đúng command với cùng `GRPO_OUTPUT_DIR`, giữ nguyên
model/dataset/hyperparameter và đổi `GRPO_RESUME=true`. Dùng suffix mới cho mỗi
run full độc lập; không trỏ một output directory cũ vào lần chạy mới.

## 15. OOM và performance tuning

Thứ tự giảm tài nguyên khuyến nghị:

1. Giảm GRPO_GENERATION_BATCH_SIZE từ 4 xuống 2.
2. Đồng thời giảm NUM_GENERATIONS từ 4 xuống 2.
3. Nếu vẫn OOM, giảm MAX_COMPLETION_LENGTH từ 3.072 xuống 2.048 và theo dõi tỷ lệ bị cắt (3/414 tool call tham chiếu vượt 2.048).
4. Giữ PER_DEVICE_TRAIN_BATCH_SIZE=1.
5. Tăng gradient accumulation nếu cần giữ effective update size.
6. Giảm RL_REWARD_RENDER_WORKERS nếu RAM CPU hoặc Chrome không ổn định.
7. Đặt REWARD_MODEL_DEVICE=cpu nếu GPU memory dành cho policy không đủ.

Ràng buộc:

- NUM_GENERATIONS phải ít nhất bằng 2.
- GRPO_GENERATION_BATCH_SIZE phải chia hết cho NUM_GENERATIONS.
- Generation batch phải chia hết cho global train batch.
- Với multi-GPU, cần tính lại theo world size.

Cấu hình OOM-safe:

    NUM_GENERATIONS=2
    GRPO_GENERATION_BATCH_SIZE=2
    MAX_COMPLETION_LENGTH=2048
    PER_DEVICE_TRAIN_BATCH_SIZE=1
    GRADIENT_ACCUMULATION_STEPS=16

## 16. Tiêu chí đánh giá một run tốt

Một run được xem là đủ tốt để tiếp tục khi:

- Invalid reward rate giảm theo thời gian.
- Mean train reward tăng nhưng không tách quá xa eval reward.
- Semantic và lexical preservation không giảm để đổi lấy aesthetics.
- DOM score không có xu hướng âm.
- Completion không bị truncate hàng loạt.
- Entropy không collapse quá sớm.
- Gradient norm hữu hạn và không spike kéo dài.
- Nhóm reward variance bằng 0 không nhận advantage chéo prompt.
- Resume tái lập đúng global step và learning rate.
- Rendered samples kiểm tra thủ công vẫn đúng nội dung, dễ đọc và đúng layout.

## 17. Rủi ro và giới hạn hiện tại

### Corpus nhỏ

49 documents là đủ cho pilot nhưng nhỏ cho một full run dài. 500 steps có thể
overfit. Evaluation document split và checkpoint selection phải được dùng để
phát hiện sớm.

### Legacy image provenance

Image URL cũ chỉ là provenance/candidate. Manifest v2 lưu candidate thực tế,
confidence và lý do Qwen-VL theo từng slot. Search vẫn phụ thuộc chất lượng nguồn;
cần kiểm tra mẫu render, còn slot hỏng/bị reject sẽ đưa cả slide về no-image.

### Serialized versus native transport

Training dùng serialized tool-call tags, production dùng native tool-call
transport. Tool schema và semantics giống nhau, nhưng vẫn có một khoảng cách
transport nhỏ cần theo dõi bằng production evaluation.

### Reward calibration

Weights hiện tại là baseline engineering hợp lý, chưa phải kết quả hyperparameter
search. Pilot 10 và calibration 50 steps là bắt buộc trước khi tin tưởng full
500-step run.

### Single-H100 default

Default được cấu hình cho một H100. Trainer tính steps-per-generation theo world
size và factor DAPO `gradient_accumulation_steps / steps_per_generation`;
multi-GPU vẫn cần pilot để kiểm tra VRAM và throughput.

## 18. Trạng thái verification

### Đã xác minh trong worktree hiện tại

- API Qwen thật trả lời text, structured output, vision và native tool call thành công.
- Rebuild smoke hai slide đã chạy planner, tìm ảnh, duyệt ảnh, lưu cache và refine; loader đọc được corpus, giữ nguyên nội dung nguồn, với hai ảnh đã duyệt. Smoke corpus nằm ở `/tmp/grpo_be_synced_smoke.json`, không phải corpus train mặc định.
- 236 test backend và RL đã đạt trước lần thêm guard CUDA cuối; guard và tài liệu ở lượt này chưa chạy lại test suite.
- FE preview, Chromium và ViT preflight đã chạy thành công trên máy phát triển trong vòng kiểm tra trước. Điều này không thay thế preflight trên H100 vì endpoint FE, browser và file ViT ở đó có thể khác.
- Source loader trước đó đọc được 49 tài liệu và 414 slide. Đây là kích thước corpus nguồn; corpus GRPO mới đầy đủ chưa được rebuild.

### Còn phải hoàn tất trước full run

- Rebuild đủ corpus GRPO mới và chuyển JSON cùng `static/output/grpo_image_cache/` lên H100.
- Trên H100, xác nhận đường dẫn local của Qwen3-8B và ViT, FE preview/Chromium, retriever và cache ảnh qua preflight mặc định.
- Chạy một optimizer step, xác nhận loss/reward/grad hữu hạn, checkpoint lưu và resume được; sau đó chạy pilot 10 bước và calibration 50 bước như kế hoạch. VRAM/throughput chưa được đo trên H100.
- Trainer hiện dừng sớm nếu CUDA không khả dụng; chỉ chạy CPU khi đặt `USE_CPU=true` tường minh cho chẩn đoán nhỏ.

Không khởi chạy job 500 bước trước khi các mục trên đạt.

## 19. Checklist trước full run

- [ ] TRAINING_MODEL_ID trỏ đúng local base model.
- [ ] REWARD_MODEL_PATH trỏ đúng checkpoint ViT.
- [ ] Chromium launch được từ user chạy job.
- [ ] Dataset snapshot có đúng số document và prompt.
- [ ] Pilot 1 step tạo checkpoint hoàn chỉnh.
- [ ] Resume từ checkpoint pilot thành công.
- [ ] Pilot 10 steps không OOM/NaN.
- [ ] Cache manifest có asset hợp lệ và train/eval snapshots có image_mode=semantic
      cho các slide đã cache.
- [ ] Invalid rate không chiếm toàn bộ rollout.
- [ ] Eval reward không giảm liên tục.
- [ ] Kiểm tra thủ công một batch slide render.
- [ ] Disk đủ cho checkpoints, logs và FAISS cache.
- [ ] Chỉ sau đó mới chạy 50-step calibration và 500-step full training.
