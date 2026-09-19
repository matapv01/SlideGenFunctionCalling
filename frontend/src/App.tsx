import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { createBrowserRouter, Outlet, RouterProvider } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AdminRoute } from "@/components/AdminRoute";
import GlobalThemeToggle from "@/components/GlobalThemeToggle";
import { SlideGenerationProvider } from "./features/slidegenius/SlideGenerationContext";

import StructureEditor from "./pages/StructureEditor";
import PresentationMode from "./pages/PresentationMode";
import XmlSlideEditor from "./pages/XmlSlideEditor";
import XmlRenderPreview from "./pages/XmlRenderPreview";
import NotFound from "./pages/NotFound";
import SlidegeniusAuth from "./features/slidegenius/SlidegeniusAuth";
import { SlidegeniusHome, SlidegeniusLanding, SlidegeniusProjectView } from "./features/slidegenius";
import AdminUsagePage from "./features/admin/AdminUsagePage";

// Context Providers Wrapper
const ProvidersLayout = () => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <SlideGenerationProvider>
            <TooltipProvider>
              <Toaster />
              <GlobalThemeToggle />
              <Outlet />
            </TooltipProvider>
          </SlideGenerationProvider>
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <ProvidersLayout />,
    children: [
      { index: true, element: <SlidegeniusLanding /> },
      { path: "home", element: <ProtectedRoute><SlidegeniusHome /></ProtectedRoute> },
      { path: "login", element: <SlidegeniusAuth mode="signin" /> },
      { path: "register", element: <SlidegeniusAuth mode="signup" /> },
      { path: "guide", element: <ProtectedRoute><SlidegeniusHome initialTab="guide" /></ProtectedRoute> },
      { path: "manual", element: <ProtectedRoute><SlidegeniusHome initialTab="manual" /></ProtectedRoute> },
      { path: "projects", element: <ProtectedRoute><SlidegeniusHome initialTab="projects" /></ProtectedRoute> },
      { path: "structure", element: <ProtectedRoute><StructureEditor /></ProtectedRoute> },
      { path: "structure/:projectId", element: <ProtectedRoute><StructureEditor /></ProtectedRoute> },
      { path: "structure/*", element: <ProtectedRoute><StructureEditor /></ProtectedRoute> },
      { path: "present/:projectId", element: <ProtectedRoute><PresentationMode /></ProtectedRoute> },
      { path: "projects/:projectId", element: <ProtectedRoute><SlidegeniusProjectView /></ProtectedRoute> },
      { path: "settings", element: <ProtectedRoute><SlidegeniusHome initialTab="settings" /></ProtectedRoute> },
      { path: "subscription", element: <ProtectedRoute><SlidegeniusHome initialTab="subscription" /></ProtectedRoute> },
      { path: "admin", element: <AdminRoute><AdminUsagePage /></AdminRoute> },
      { path: "editor", element: <ProtectedRoute><XmlSlideEditor /></ProtectedRoute> },
      { path: "render/xml-preview", element: <XmlRenderPreview /> },
      { path: "*", element: <NotFound /> },
    ]
  }
], { basename: "/slidegen" });

const App = () => <RouterProvider router={router} />;

export default App;
