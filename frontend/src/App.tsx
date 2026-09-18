import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { createBrowserRouter, Navigate, Outlet, RouterProvider, useParams } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { SlideGenerationProvider } from "./features/slidegenius/SlideGenerationContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import StructureEditor from "./pages/StructureEditor";
import PresentationMode from "./pages/PresentationMode";
import XmlSlideEditor from "./pages/XmlSlideEditor";
import XmlRenderPreview from "./pages/XmlRenderPreview";
import NotFound from "./pages/NotFound";
import { SlidegeniusHome, SlidegeniusLanding, SlidegeniusProjectView } from "./features/slidegenius";

// Context Providers Wrapper
const ProvidersLayout = () => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <SlideGenerationProvider>
            <TooltipProvider>
              <Toaster />
              <Outlet />
            </TooltipProvider>
          </SlideGenerationProvider>
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
};

const LegacyEditorRedirect = () => {
  const { projectId } = useParams();
  return <Navigate replace to={projectId ? `/editor?project=${projectId}` : "/projects"} />;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <ProvidersLayout />,
    children: [
      { index: true, element: <SlidegeniusLanding /> },
      { path: "home", element: <ProtectedRoute><SlidegeniusHome /></ProtectedRoute> },
      // One user-facing generation workflow now lives in the chatbot. Keep
      // this old URL as a safe entry point for bookmarks without exposing the
      // legacy Doc/Idea selector.
      { path: "create-slides", element: <Navigate replace to="/home" /> },
      { path: "login", element: <Login /> },
      { path: "register", element: <Register /> },
      { path: "guide", element: <ProtectedRoute><SlidegeniusHome initialTab="guide" /></ProtectedRoute> },
      { path: "manual", element: <ProtectedRoute><SlidegeniusHome initialTab="manual" /></ProtectedRoute> },
      { path: "projects", element: <ProtectedRoute><SlidegeniusHome initialTab="projects" /></ProtectedRoute> },
      // Generation progress is rendered by the shared right-side drawer now.
      // Keep the old URL as a bookmark-safe redirect without exposing the
      // retired full-page Streaming UI.
      { path: "streaming/:projectId", element: <Navigate replace to="/home" /> },
      { path: "structure", element: <ProtectedRoute><StructureEditor /></ProtectedRoute> },
      { path: "structure/:projectId", element: <ProtectedRoute><StructureEditor /></ProtectedRoute> },
      { path: "structure/*", element: <ProtectedRoute><StructureEditor /></ProtectedRoute> },
      { path: "editor/:projectId", element: <ProtectedRoute><LegacyEditorRedirect /></ProtectedRoute> },
      { path: "present/:projectId", element: <ProtectedRoute><PresentationMode /></ProtectedRoute> },
      { path: "projects/:projectId", element: <ProtectedRoute><SlidegeniusProjectView /></ProtectedRoute> },
      { path: "settings", element: <ProtectedRoute><SlidegeniusHome initialTab="settings" /></ProtectedRoute> },
      { path: "subscription", element: <ProtectedRoute><SlidegeniusHome initialTab="subscription" /></ProtectedRoute> },
      { path: "editor", element: <ProtectedRoute><XmlSlideEditor /></ProtectedRoute> },
      { path: "render/xml-preview", element: <XmlRenderPreview /> },
      { path: "*", element: <NotFound /> },
    ]
  }
], { basename: "/slidegen" });

const App = () => <RouterProvider router={router} />;

export default App;
