import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import CoursesPage from "./pages/CoursesPage";
import InstructorsPage from "./pages/InstructorsPage";
import LessonPage from "./pages/LessonPage";
import TestMui from "./pages/TestMui.tsx";

export default function App() {
  return (
    <Router>
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/instructors" element={<InstructorsPage />} />
            <Route path="/lesson/:id" element={<LessonPage />} />
            <Route path='/test' element={<TestMui />} />
        </Routes>
    </Router>
  );
}
