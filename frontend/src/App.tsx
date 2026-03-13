import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
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
import SlideEditor from "./pages/SlideEditor";
import PresentationMode from "./pages/PresentationMode";
import ViewProject from "./pages/ViewProject";
import Guide from "./pages/Guide";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Context Providers Wrapper
const ProvidersLayout = () => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <Outlet />
          </TooltipProvider>
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
};

const router = createBrowserRouter([
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
      { path: "/editor/:projectId", element: <ProtectedRoute><SlideEditor /></ProtectedRoute> },
      { path: "/present/:projectId", element: <ProtectedRoute><PresentationMode /></ProtectedRoute> },
      { path: "/view/:projectId", element: <ProtectedRoute><ViewProject /></ProtectedRoute> },
      { path: "/settings", element: <ProtectedRoute><Settings /></ProtectedRoute> },
      { path: "*", element: <NotFound /> },
    ]
  }
]);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <RouterProvider router={router} />
  </QueryClientProvider>
);

export default App;
