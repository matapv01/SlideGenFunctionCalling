import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
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
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/slidegen" element={<SlideGen />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/guide" element={<Guide />} />
              <Route path="/projects" element={<ProtectedRoute><Projects /></ProtectedRoute>} />
              <Route path="/streaming/:projectId" element={<ProtectedRoute><Streaming /></ProtectedRoute>} />
              <Route path="/structure" element={<ProtectedRoute><StructureEditor /></ProtectedRoute>} />
              <Route path="/editor/:projectId" element={<ProtectedRoute><SlideEditor /></ProtectedRoute>} />
              <Route path="/present/:projectId" element={<ProtectedRoute><PresentationMode /></ProtectedRoute>} />
              <Route path="/view/:projectId" element={<ProtectedRoute><ViewProject /></ProtectedRoute>} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
