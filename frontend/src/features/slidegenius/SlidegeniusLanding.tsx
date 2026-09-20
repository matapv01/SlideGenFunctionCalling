import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import SlidegenLogo from "@/components/SlidegenLogo";
import { publicAssetUrl } from "@/lib/publicAssetUrl";
import "./slidegenius.css";

const categories = ([
  { eyebrow: ["01 / CHAT", "01 / CHAT"], label: ["Slidegenius", "Slidegenius"], title: ["Start with a rough idea.", "Bắt đầu từ một ý tưởng thô."], copy: ["Describe the story in natural language and let Slidegenius shape the brief, structure, and direction.", "Mô tả câu chuyện bằng ngôn ngữ tự nhiên để Slidegenius định hình brief, cấu trúc và hướng triển khai."], tone: "light" },
  { eyebrow: ["02 / DOCX", "02 / DOCX"], label: ["Document to deck", "Từ tài liệu đến slide"], title: ["Bring the source material in.", "Đưa tài liệu gốc vào."], copy: ["Upload a DOCX, ground the conversation in your content, and turn dense material into a clear presentation.", "Tải DOCX lên, đặt cuộc trò chuyện trên nền nội dung của bạn và biến tài liệu dày thành bài trình bày rõ ràng."], tone: "dark" },
  { eyebrow: ["03 / MANUAL", "03 / THỦ CÔNG"], label: ["Structure editor", "Structure editor"], title: ["Shape the story yourself.", "Tự định hình câu chuyện."], copy: ["Edit the Markdown structure, review each slide, then send the approved outline to the design engine.", "Chỉnh cấu trúc Markdown, xem trước từng slide rồi gửi outline đã duyệt đến bộ máy thiết kế."], tone: "sand" },
  { eyebrow: ["04 / EDITOR", "04 / BIÊN TẬP"], label: ["XML slide editor", "XML slide editor"], title: ["Make every slide yours.", "Biến từng slide thành của bạn."], copy: ["Fine-tune text, shapes, images, equations, layers, notes, and transitions in the editable workspace.", "Tinh chỉnh text, shape, hình ảnh, công thức, layer, ghi chú và hiệu ứng chuyển cảnh trong workspace."], tone: "coral" },
  { eyebrow: ["05 / PRESENT", "05 / TRÌNH CHIẾU"], label: ["Present and export", "Trình chiếu và xuất file"], title: ["Take the deck all the way.", "Hoàn thiện deck đến bước cuối."], copy: ["Present in fullscreen, collaborate with your team, keep versions, and export when the story is ready.", "Trình chiếu toàn màn hình, cộng tác cùng team, lưu phiên bản và xuất file khi câu chuyện đã sẵn sàng."], tone: "ink" },
] as const).filter((category) => category.label[0] !== "XML slide editor");

const typingPrompts = { en: ["What do you want to create?", "A bold pitch deck for tomorrow", "A story your audience remembers"], vi: ["Bạn muốn tạo ra điều gì?", "Một bài gọi vốn ấn tượng cho ngày mai", "Một câu chuyện khán giả sẽ nhớ mãi"] };

export default function SlidegeniusLanding() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { language, setLanguage } = useLanguage();
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const closeTimer = useRef<number | null>(null);
  const [promptIndex, setPromptIndex] = useState(0);
  const [typedPrompt, setTypedPrompt] = useState("");
  const [prompt, setPrompt] = useState("");
  const [newsletterEmail, setNewsletterEmail] = useState("");
  const isVietnamese = language === "vi";

  useEffect(() => {
    const phrase = typingPrompts[language][promptIndex];
    let position = 0;
    let deleting = false;
    let timer = 0;
    const tick = () => {
      if (!deleting && position < phrase.length) position += 1;
      else if (deleting && position > 0) position -= 1;
      else if (!deleting) deleting = true;
      else { deleting = false; setPromptIndex((index) => (index + 1) % typingPrompts[language].length); }
      setTypedPrompt(phrase.slice(0, position));
      timer = window.setTimeout(tick, !deleting && position === phrase.length ? 1500 : deleting ? 42 : 68);
    };
    timer = window.setTimeout(tick, 420);
    return () => window.clearTimeout(timer);
  }, [language, promptIndex]);

  useEffect(() => {
    const cards = Array.from(document.querySelectorAll<HTMLElement>('.sgl-landing .feature-stage'));
    if (!cards.length) return undefined;

    if (!('IntersectionObserver' in window)) {
      cards.forEach((card) => card.classList.add('is-visible'));
      return undefined;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.16 });

    cards.forEach((card) => observer.observe(card));
    return () => observer.disconnect();
  }, []);

  const openMenuSmoothly = (menu: string) => {
    if (closeTimer.current !== null) window.clearTimeout(closeTimer.current);
    setOpenMenu(menu);
  };
  const closeMenuSmoothly = () => {
    if (closeTimer.current !== null) window.clearTimeout(closeTimer.current);
    closeTimer.current = window.setTimeout(() => setOpenMenu(null), 180);
  };
  const handlePromptSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    navigate(isAuthenticated ? "/home" : "/register");
  };
  const handleNewsletterSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const email = newsletterEmail.trim();
    navigate(email ? `/register?email=${encodeURIComponent(email)}` : "/register");
  };

  return (
    <main className="sgl-landing slidegen-page">
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Slidegen home"><SlidegenLogo /></a>
        <nav className="main-nav" aria-label="Main navigation">
          <div className="nav-menu" onMouseEnter={() => openMenuSmoothly("product")} onMouseLeave={closeMenuSmoothly}><button type="button" aria-expanded={openMenu === "product"} onClick={() => openMenuSmoothly("product")}>{isVietnamese ? "Sản phẩm" : "Product"}<span className="nav-chevron" /></button>{openMenu === "product" && <div className="mega-menu product-menu"><div className="mega-column"><p>{isVietnamese ? "Nền tảng cốt lõi" : "Core platform"}</p><a href="#templates"><i>◉</i><span><b>{isVietnamese ? "Ứng dụng web" : "Web app"}</b><small>{isVietnamese ? "Tạo ngay trên trình duyệt" : "Create in your browser"}</small></span></a><a href="#templates"><i>▣</i><span><b>{isVietnamese ? "Ứng dụng máy tính" : "Desktop app"}</b><small>{isVietnamese ? "Làm việc trên mọi màn hình" : "Work across every screen"}</small></span></a><a href="#templates"><i>API</i><span><b>API / CLI</b><small>{isVietnamese ? "Xây dựng cùng Slidegen" : "Build with Slidegen"}</small></span></a></div><div className="mega-column"><p>{isVietnamese ? "Công cụ sáng tạo" : "Creation tools"}</p><a href="#templates"><i>⌁</i><span><b>{isVietnamese ? "Bảng sáng tạo" : "Canvas"}</b><small>{isVietnamese ? "Định hình ý tưởng bằng hình ảnh" : "Shape ideas visually"}</small></span></a><a href="#templates"><i>▦</i><span><b>{isVietnamese ? "Mẫu thiết kế" : "Templates"}</b><small>{isVietnamese ? "Bắt đầu từ nền tảng vững chắc" : "Start from a strong point"}</small></span></a><a href="#templates"><i>✦</i><span><b>{isVietnamese ? "Không gian thử nghiệm" : "Playground"}</b><small>{isVietnamese ? "Tự do thử nghiệm" : "Experiment freely"}</small></span></a></div><div className="mega-column"><p>{isVietnamese ? "Tích hợp" : "Integrations"}</p><a href="#templates"><i>◉</i><span><b>Figma</b><small>{isVietnamese ? "Đưa hệ thống của bạn vào" : "Bring your systems in"}</small></span></a><a href="#templates"><i>✣</i><span><b>Slack</b><small>{isVietnamese ? "Cộng tác đúng ngữ cảnh" : "Collaborate in context"}</small></span></a><a href="#templates"><i>↗</i><span><b>Notion</b><small>{isVietnamese ? "Biến ghi chú thành bài trình bày" : "Turn notes into decks"}</small></span></a></div><a className="mega-feature" href="#templates"><div className="feature-preview"><span>SLIDEGEN</span><strong>{isVietnamese ? <>Bảng sáng tạo<br />cho mọi câu chuyện.</> : <>Creative canvas<br />for every story.</>}</strong><em>↗</em></div><b>{isVietnamese ? "Ứng dụng web" : "Web app"}</b><small>{isVietnamese ? "Bắt đầu tạo cùng Slidegen chỉ trong vài giây trên trình duyệt" : "Start creating with Slidegen in seconds, right in your browser"}</small></a></div>}</div>
          <a href="#templates">{isVietnamese ? "Mẫu thiết kế" : "Templates"}</a>
          <div className="nav-menu" onMouseEnter={() => openMenuSmoothly("resources")} onMouseLeave={closeMenuSmoothly}><button type="button" aria-expanded={openMenu === "resources"} onClick={() => openMenuSmoothly("resources")}>{isVietnamese ? "Tài nguyên" : "Resources"}<span className="nav-chevron" /></button>{openMenu === "resources" && <div className="mega-menu compact-mega"><div className="mega-column"><p>{isVietnamese ? "Khám phá Slidegen" : "Explore Slidegen"}</p><a href="#templates"><i>✦</i><span><b>{isVietnamese ? "Cảm hứng" : "Inspiration"}</b><small>{isVietnamese ? "Khám phá những sản phẩm ấn tượng" : "See what great work looks like"}</small></span></a><a href="#templates"><i>▧</i><span><b>{isVietnamese ? "Hướng dẫn" : "Guides"}</b><small>{isVietnamese ? "Ý tưởng thực tế cho bài trình bày tốt hơn" : "Practical ideas for better decks"}</small></span></a><a href="#templates"><i>↗</i><span><b>{isVietnamese ? "Câu chuyện khách hàng" : "Customer stories"}</b><small>{isVietnamese ? "Gặp gỡ những đội ngũ tạo ra khác biệt" : "Meet teams making an impact"}</small></span></a></div><div className="mega-column"><p>{isVietnamese ? "Học cùng chúng tôi" : "Learn with us"}</p><a href="#templates"><i>◌</i><span><b>Blog</b><small>Fresh thinking for creative teams</small></span></a><a href="#templates"><i>?</i><span><b>Help center</b><small>Find your way around Slidegen</small></span></a></div><a className="mega-feature" href="#templates"><div className="feature-preview"><span>SLIDEGEN / FIELD NOTES</span><strong>{isVietnamese ? <>Ý tưởng đáng<br />chia sẻ.</> : <>Ideas worth<br />sharing.</>}</strong><em>↗</em></div><b>{isVietnamese ? "Tài nguyên sáng tạo" : "Creative resources"}</b><small>{isVietnamese ? "Góc nhìn mới cho mọi câu chuyện bạn kể" : "New perspectives for every story you tell"}</small></a></div>}</div>
          <div className="nav-menu" onMouseEnter={() => openMenuSmoothly("company")} onMouseLeave={closeMenuSmoothly}><button type="button" aria-expanded={openMenu === "company"} onClick={() => openMenuSmoothly("company")}>{isVietnamese ? "Công ty" : "Company"}<span className="nav-chevron" /></button>{openMenu === "company" && <div className="mega-menu compact-mega"><div className="mega-column"><p>{isVietnamese ? "Về Slidegen" : "About Slidegen"}</p><a href="#create"><i>◎</i><span><b>{isVietnamese ? "Câu chuyện của chúng tôi" : "Our story"}</b><small>{isVietnamese ? "Vì sao chúng tôi xây dựng cho đội ngũ sáng tạo" : "Why we build for creative teams"}</small></span></a><a href="#create"><i>⌁</i><span><b>{isVietnamese ? "Tuyển dụng" : "Careers"}</b><small>{isVietnamese ? "Cùng định hình tương lai công việc" : "Help shape the future of work"}</small></span></a><a href="#create"><i>↗</i><span><b>{isVietnamese ? "Liên hệ" : "Contact"}</b><small>{isVietnamese ? "Hãy cùng tạo nên điều gì đó" : "Let's make something together"}</small></span></a></div><div className="mega-column"><p>{isVietnamese ? "Kết nối cùng chúng tôi" : "Stay connected"}</p><a href="#create"><i>◎</i><span><b>{isVietnamese ? "Tạp chí" : "Journal"}</b><small>{isVietnamese ? "Ghi chú từ studio" : "Notes from the studio"}</small></span></a><a href="#create"><i>+</i><span><b>{isVietnamese ? "Bản tin" : "Newsletter"}</b><small>{isVietnamese ? "Tư duy sáng tạo gửi đến bạn" : "Creative thinking, delivered"}</small></span></a></div><a className="mega-feature" href="#create"><div className="feature-preview"><span>SLIDEGEN / STUDIO</span><strong>{isVietnamese ? <>Cùng nhau tạo<br />giá trị tốt hơn.</> : <>Make better<br />work, together.</>}</strong><em>↗</em></div><b>{isVietnamese ? "Gặp gỡ đội ngũ" : "Meet the team"}</b><small>{isVietnamese ? "Con người, quy trình và ý tưởng phía sau Slidegen" : "People, process, and the ideas behind Slidegen"}</small></a></div>}</div>
          <Link to="/subscription">{isVietnamese ? "Bảng giá" : "Pricing"}</Link>
        </nav>
        <div className="header-actions"><button className="language-switcher" type="button" aria-label="Switch language" onClick={() => setLanguage(language === "en" ? "vi" : "en")}><span className={!isVietnamese ? "is-active" : ""}>EN</span><span>/</span><span className={isVietnamese ? "is-active" : ""}>VI</span></button>{isAuthenticated ? <Link to="/home">Workspace</Link> : <Link to="/login">Sign In</Link>} {!isAuthenticated && <Link className="start-button" to="/register">{isVietnamese ? "Bắt đầu miễn phí" : "Start for Free"}</Link>}</div>
      </header>
      <section id="top" className="hero" style={{ backgroundImage: `url("${publicAssetUrl("bgslidegen-poster.png")}")` }}>
        <video className="hero-background-video" autoPlay muted loop playsInline preload="auto" poster={publicAssetUrl("bgslidegen-poster.png")} aria-label="Slidegen animated background">
          <source src={publicAssetUrl("bgslidegen.mp4")} type="video/mp4" />
        </video>
        <div className="hero-video-overlay" />
        <p className="hero-topline">{isVietnamese ? "BIẾN Ý TƯỞNG THÀNH SLIDE" : "TURN IDEAS INTO SLIDES"}</p>
        <div className="dot-grid" />
        <div className="hero-copy">
          {isVietnamese
            ? <>Workspace AI cho bài trình bày.<br />Từ brief, DOCX đến deck có thể chỉnh sửa.</>
            : <>An AI workspace for presentations.<br />From brief and DOCX to an editable deck.</>}
        </div>
        <form className="prompt-wrap" onSubmit={handlePromptSubmit}>
          <div className="prompt-field">
            <input className="landing-prompt-input" type="text" value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder={typedPrompt} aria-label={isVietnamese ? "Bạn muốn tạo gì?" : "What do you want to create?"} />
          </div>
          <button className="signup" type="submit">{isVietnamese ? "Mở workspace" : "Open workspace"}<span>↗</span></button>
        </form>
      </section>
      <section id="templates" className="showcase-section"><div className="section-intro"><p>{isVietnamese ? "MỘT STUDIO. MỌI CÂU CHUYỆN." : "ONE STUDIO. EVERY STORY."}</p><h2>{isVietnamese ? "Ý tưởng chuyển động." : "Ideas, in motion."}</h2><span>{isVietnamese ? "Một hệ thống sáng tạo linh hoạt cho mọi cách đội ngũ của bạn muốn truyền đạt." : "One flexible creative system for every way your team needs to communicate."}</span></div><div className="feature-list">{categories.map((category, index) => { const value = isVietnamese ? 1 : 0; const sourceLabels = isVietnamese ? ["BRIEF", "DOCX", "MARKDOWN", "CANVAS", "DECK"] : ["BRIEF", "DOCX", "MARKDOWN", "CANVAS", "DECK"]; const cardNumber = category.eyebrow[0].slice(0, 2); return <article className={`feature-stage tone-${category.tone}`} key={category.label[value]}><div className="feature-copy"><p>{category.eyebrow[value]}</p><h3 className="title-unified">{category.title[value]}</h3><span>{category.copy[value]}</span><a href="#create">{isVietnamese ? "Khám phá Slidegen" : "Explore Slidegen"}<b>↗</b></a></div><div className={`feature-canvas feature-canvas-${index}`}><div className="canvas-grid" /><div className="canvas-label">SLIDEGEN / {cardNumber}</div><div className="canvas-title">{category.label[value]}</div><div className="canvas-subtitle">{category.title[value]}</div><div className="canvas-visual" aria-hidden="true"><div className="visual-source"><span>SOURCE</span><strong>{sourceLabels[index]}</strong><i /><i /><i /></div><div className="visual-connector"><span>→</span><i /></div><div className="visual-deck"><span>SLIDEGENIUS</span><strong>{isVietnamese ? "Deck sẵn sàng" : "Deck ready"}</strong><div><i /><i /><i /></div></div></div></div></article>; })}</div></section>
      <section id="create" className="create-section"><div><p>SLIDEGEN FOR CREATIVE TEAMS</p><h2 className="title-unified">{isVietnamese ? <>Khiến ý tưởng<br /><em>không thể bị bỏ qua.</em></> : <>Make the idea<br /><em>impossible to ignore.</em></>}</h2><a href="#top">{isVietnamese ? "Bắt đầu sáng tạo" : "Start creating"}<span>↗</span></a></div><div className="newsletter"><p>{isVietnamese ? "ĐỪNG BỎ LỠ" : "STAY IN THE LOOP"}</p><strong>{isVietnamese ? "Tư duy sáng tạo, gửi đến bạn." : "Creative thinking, delivered."}</strong><form onSubmit={handleNewsletterSubmit}><input aria-label="Email address" name="newsletter-email" placeholder={isVietnamese ? "Địa chỉ email của bạn" : "Your email address"} type="email" value={newsletterEmail} onChange={(event) => setNewsletterEmail(event.target.value)} required /><button type="submit">{isVietnamese ? "Tham gia" : "Join"}<span>↗</span></button></form></div></section>
      <footer className="site-footer">
        <div className="footer-top">
          <div className="footer-brand">
            <a className="brand" href="#top" aria-label="Slidegen home"><SlidegenLogo /></a>
            <span>{isVietnamese ? "Cùng nhau tạo nên công việc tốt hơn." : "Make better work, together."}</span>
            <a className="footer-cta" href="#create">{isVietnamese ? "Bắt đầu sáng tạo" : "Start creating"}<span>↗</span></a>
          </div>
          <div className="footer-links">
            <div><b>Product</b><a href="#templates">Presentations</a><a href="#templates">Pitch decks</a><a href="#templates">Reports</a></div>
            <div><b>Company</b><a href="#top">About</a><a href="#top">Careers</a><a href="#top">Contact</a></div>
            <div><b>Social</b><a href="#top">Instagram</a><a href="#top">LinkedIn</a><a href="#top">X / Twitter</a></div>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© 2026 Slidegen</span>
          <span className="footer-status"><i />All systems go</span>
          <span className="footer-legal"><a href="#top">Privacy</a><span>·</span><a href="#top">Terms</a></span>
        </div>
      </footer>
    </main>
  );
}
