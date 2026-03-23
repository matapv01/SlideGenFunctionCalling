import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { createBrowserRouter, RouterProvider, Outlet } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

import Home from "./pages/Home";
import SlideGen from "./pages/SlideGen";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Projects from "./pages/Projects";
import Streaming from "./pages/Streaming";
import StructureEditor from "./pages/StructureEditor";
import IdeaStructure from "./pages/IdeaStructure";
import SlideEditor from "./pages/SlideEditor";
import PresentationMode from "./pages/PresentationMode";
import ViewProject from "./pages/ViewProject";
import Guide from "./pages/Guide";
import Settings from "./pages/Settings";
import Subscription from "./pages/Subscription";
import NotFound from "./pages/NotFound";

// Context Providers Wrapper
const ProvidersLayout = () => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <TooltipProvider>
            <Toaster />
            <Outlet />
          </TooltipProvider>
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
};

const router = createBrowserRouter(
  [
    {
      element: <ProvidersLayout />,
      children: [
        { path: "/", element: <Home /> },
        { path: "/slidegen", element: <SlideGen /> },
        { path: "/login", element: <Login /> },
        { path: "/register", element: <Register /> },
        { path: "/guide", element: <Guide /> },
        { path: "/projects", element: <ProtectedRoute><Projects /></ProtectedRoute> },
        { path: "/streaming/:projectId", element: <ProtectedRoute><Streaming /></ProtectedRoute> },
        { path: "/structure/:projectId", element: <ProtectedRoute><StructureEditor /></ProtectedRoute> },
        { path: "/idea/structure/:sessionId", element: <ProtectedRoute><IdeaStructure /></ProtectedRoute> },
        { path: "/editor/:projectId", element: <ProtectedRoute><SlideEditor /></ProtectedRoute> },
        { path: "/present/:projectId", element: <ProtectedRoute><PresentationMode /></ProtectedRoute> },
        { path: "/view/:projectId", element: <ProtectedRoute><ViewProject /></ProtectedRoute> },
        { path: "/settings", element: <ProtectedRoute><Settings /></ProtectedRoute> },
        { path: "/subscription", element: <ProtectedRoute><Subscription /></ProtectedRoute> },
        { path: "*", element: <NotFound /> },
      ]
    }
  ],
);

const App = () => <RouterProvider router={router} />;

export default App;
