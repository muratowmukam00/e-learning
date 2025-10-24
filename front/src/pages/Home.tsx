import Hero from '../components/Hero';
import Features from '../components/Features';
import AboutSection from '../components/AboutSection';
import CTA from '../components/CTA';
import Pricing from '../components/Pricing';
import Testimonials from '../components/Testimonials';
import FAQ from '../components/FAQ';
import Team from '../components/Team';
import Blog from '../components/Blog';
import ContactSection from '../components/ContactSection';
import BackToTop from '../components/BackToTop';

const Home = () => {
  return (
    <>
      <Hero />
      <Features />
      <AboutSection />
      <CTA />
      <Pricing />
      <Testimonials />
      <FAQ />
      <Team />
      <Blog />
      <ContactSection />
      <BackToTop />
    </>
  );
};

export default Home;
