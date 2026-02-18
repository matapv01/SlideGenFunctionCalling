import { useNavigate } from "react-router-dom";
import {
  Sparkles,
  ArrowRight,
  Zap,
  Palette,
  Clock,
  Globe,
  Users,
  Star,
  CheckCircle,
  Play,
  ChevronDown,
  Rocket,
  Heart,
  Award,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ThemeToggle } from "@/components/ThemeToggle";

const features = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Generate professional slides in seconds with our AI-powered engine",
    gradient: "from-yellow-400 to-orange-500",
  },
  {
    icon: Palette,
    title: "Beautiful Designs",
    description: "Stunning templates and themes crafted by professional designers",
    gradient: "from-pink-500 to-rose-500",
  },
  {
    icon: Clock,
    title: "Save Hours",
    description: "What used to take hours now takes minutes. Focus on what matters",
    gradient: "from-cyan-400 to-blue-500",
  },
  {
    icon: Globe,
    title: "Multi-Language",
    description: "Create presentations in any language with intelligent text processing",
    gradient: "from-green-400 to-emerald-500",
  },
];

const stats = [
  { value: "10K+", label: "Presentations Created" },
  { value: "99%", label: "Satisfaction Rate" },
  { value: "50+", label: "Templates Available" },
  { value: "24/7", label: "AI Availability" },
];

const sponsors = [
  { name: "TechCorp", logo: "🚀" },
  { name: "InnovateLab", logo: "💡" },
  { name: "DesignStudio", logo: "🎨" },
  { name: "CloudSystems", logo: "☁️" },
  { name: "DataFlow", logo: "📊" },
  { name: "CreativeAI", logo: "🤖" },
];

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Marketing Director",
    content: "SlideGen transformed how we create presentations. What took our team hours now takes minutes!",
    avatar: "👩‍💼",
  },
  {
    name: "Michael Roberts",
    role: "Startup Founder",
    content: "The AI understanding is incredible. It captures exactly what I want to communicate.",
    avatar: "👨‍💻",
  },
  {
    name: "Emily Davis",
    role: "Professor",
    content: "My students love the visual quality. SlideGen makes complex topics easy to present.",
    avatar: "👩‍🏫",
  },
];

const Home = () => {
  const navigate = useNavigate();

  const scrollToFeatures = () => {
    document.getElementById("features")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-gradient-to-br from-primary/30 to-accent/30 blur-3xl animate-blob" />
        <div className="absolute top-1/3 -left-40 h-96 w-96 rounded-full bg-gradient-to-br from-blue-500/20 to-cyan-500/20 blur-3xl animate-blob animation-delay-2000" />
        <div className="absolute -bottom-40 right-1/3 h-96 w-96 rounded-full bg-gradient-to-br from-pink-500/20 to-purple-500/20 blur-3xl animate-blob animation-delay-4000" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 backdrop-blur-xl bg-background/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-primary animate-pulse-slow">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">SlideGen</span>
            </div>
            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
              <a href="#testimonials" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Testimonials</a>
              <a href="#sponsors" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Partners</a>
            </div>
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <Button variant="ghost" size="sm" onClick={() => navigate("/login")}>
                Sign In
              </Button>
              <Button
                size="sm"
                className="gradient-primary text-white border-0 shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all hover:-translate-y-0.5"
                onClick={() => navigate("/slidegen")}
              >
                Get Started <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-2 text-sm backdrop-blur animate-fade-in">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary"></span>
              </span>
              <span className="text-primary font-medium">AI-Powered Presentation Generator</span>
            </div>

            {/* Main Headline */}
            <h1 className="mt-8 text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight animate-fade-in animation-delay-200">
              Create Stunning Slides
              <br />
              <span className="relative">
                <span className="gradient-text">In Seconds</span>
                <svg className="absolute -bottom-2 left-0 w-full" viewBox="0 0 300 12" fill="none">
                  <path d="M2 10C50 3 100 3 150 6C200 9 250 5 298 2" stroke="url(#gradient)" strokeWidth="3" strokeLinecap="round"/>
                  <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="hsl(262 83% 58%)" />
                      <stop offset="100%" stopColor="hsl(330 81% 60%)" />
                    </linearGradient>
                  </defs>
                </svg>
              </span>
            </h1>

            {/* Subtitle */}
            <p className="mt-8 mx-auto max-w-2xl text-lg sm:text-xl text-muted-foreground animate-fade-in animation-delay-400">
              Transform your documents and ideas into beautiful, professional presentations with the power of AI.
              No design skills required.
            </p>

            {/* CTA Buttons */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in animation-delay-600">
              <Button
                size="lg"
                className="group relative overflow-hidden gradient-primary text-white border-0 shadow-2xl shadow-primary/30 hover:shadow-primary/40 transition-all hover:-translate-y-1 px-8 py-6 text-lg"
                onClick={() => navigate("/slidegen")}
              >
                <span className="relative z-10 flex items-center">
                  <Rocket className="mr-2 h-5 w-5" />
                  Start Creating Free
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="group px-8 py-6 text-lg border-2 hover:bg-primary/5 hover:text-foreground"
                onClick={() => navigate("/guide")}
              >
                <Play className="mr-2 h-5 w-5 text-primary" />
                Watch Demo
              </Button>
            </div>

            {/* Stats */}
            <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 animate-fade-in animation-delay-800">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold gradient-text">{stat.value}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Scroll Indicator */}
            <button
              onClick={scrollToFeatures}
              className="mt-16 mx-auto flex flex-col items-center text-muted-foreground hover:text-foreground transition-colors animate-bounce"
            >
              <span className="text-sm">Discover More</span>
              <ChevronDown className="h-5 w-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <span className="inline-block px-3 py-1 text-sm font-medium rounded-full bg-primary/10 text-primary mb-4">
              Features
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold">
              Everything You Need to
              <span className="gradient-text"> Create Perfect Slides</span>
            </h2>
            <p className="mt-4 text-muted-foreground max-w-2xl mx-auto">
              Powerful AI capabilities combined with intuitive design tools make SlideGen the ultimate presentation companion.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="group relative overflow-hidden border-border/50 hover:border-primary/50 transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:shadow-primary/10"
              >
                <CardContent className="p-6">
                  <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${feature.gradient} shadow-lg`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm">{feature.description}</p>
                </CardContent>
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <span className="inline-block px-3 py-1 text-sm font-medium rounded-full bg-accent/10 text-accent mb-4">
              How It Works
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold">
              Three Simple Steps to
              <span className="gradient-text"> Amazing Presentations</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Upload or Describe", desc: "Upload your document or describe your presentation idea", icon: "📄" },
              { step: "02", title: "AI Magic", desc: "Our AI analyzes and creates beautiful slides instantly", icon: "✨" },
              { step: "03", title: "Export & Present", desc: "Download in multiple formats or present directly", icon: "🎯" },
            ].map((item, index) => (
              <div key={index} className="relative group">
                <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-primary to-accent opacity-0 group-hover:opacity-20 blur transition-opacity" />
                <div className="relative p-8 rounded-xl bg-card border border-border/50 text-center">
                  <div className="text-5xl mb-4">{item.icon}</div>
                  <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 text-primary text-sm font-bold mb-4">
                    {item.step}
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-muted-foreground">{item.desc}</p>
                </div>
                {index < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ArrowRight className="h-8 w-8 text-primary/30" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <span className="inline-block px-3 py-1 text-sm font-medium rounded-full bg-warning/10 text-warning mb-4">
              Testimonials
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold">
              Loved by
              <span className="gradient-text"> Thousands</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-border/50">
                <CardContent className="p-6">
                  <div className="flex items-center gap-1 text-yellow-500 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-current" />
                    ))}
                  </div>
                  <p className="text-muted-foreground mb-6 italic">"{testimonial.content}"</p>
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">{testimonial.avatar}</div>
                    <div>
                      <div className="font-semibold">{testimonial.name}</div>
                      <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Sponsors */}
      <section id="sponsors" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <span className="inline-block px-3 py-1 text-sm font-medium rounded-full bg-info/10 text-info mb-4">
              Partners & Sponsors
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold">
              Trusted by
              <span className="gradient-text"> Industry Leaders</span>
            </h2>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
            {sponsors.map((sponsor, index) => (
              <div
                key={index}
                className="group flex items-center gap-3 px-6 py-4 rounded-xl bg-card border border-border/50 hover:border-primary/50 transition-all hover:shadow-lg hover:-translate-y-1"
              >
                <span className="text-3xl">{sponsor.logo}</span>
                <span className="text-lg font-semibold text-muted-foreground group-hover:text-foreground transition-colors">
                  {sponsor.name}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <p className="text-muted-foreground">Want to become a partner?</p>
            <Button variant="link" className="text-primary">
              Contact us <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="relative overflow-hidden rounded-3xl gradient-primary p-12 text-center text-white">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjEiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')]" />
            <div className="relative">
              <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 backdrop-blur mb-6">
                <Sparkles className="h-8 w-8" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Ready to Create Amazing Presentations?
              </h2>
              <p className="text-lg text-white/80 mb-8 max-w-xl mx-auto">
                Join thousands of users who are already creating stunning slides with SlideGen.
                Start for free today!
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button
                  size="lg"
                  className="bg-white text-primary hover:bg-white/90 shadow-2xl px-8 py-6 text-lg"
                  onClick={() => navigate("/slidegen")}
                >
                  <Rocket className="mr-2 h-5 w-5" />
                  Get Started Free
                </Button>
                <Button
                  size="lg"
                  className="bg-transparent border-2 border-white/30 text-white hover:bg-white/10 hover:text-white px-8 py-6 text-lg"
                  onClick={() => navigate("/login")}
                >
                  Sign In
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg gradient-primary">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="font-semibold gradient-text">SlideGen</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
              <a href="#" className="hover:text-foreground transition-colors">Terms</a>
              <a href="#" className="hover:text-foreground transition-colors">Contact</a>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              Made with <Heart className="h-4 w-4 text-red-500 fill-red-500" /> by SlideGen Team
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
