import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  return (
    <div className={`fixed top-0 left-0 z-40 flex items-center w-full transition-all duration-300 ${
      isScrolled ? 'bg-white dark:bg-dark shadow-lg' : 'bg-transparent'
    }`}>
      <div className="container px-4 mx-auto">
        <div className="relative flex items-center justify-between -mx-4">
          <div className="max-w-full px-4 w-60">
            <Link to="/" className="block w-full py-5">
              <img
                src="/assets/images/logo/logo-white.svg"
                alt="logo"
                className={`w-full ${isScrolled ? 'hidden' : 'block'}`}
              />
              <img
                src="/assets/images/logo/logo.svg"
                alt="logo"
                className={`w-full ${isScrolled ? 'block dark:hidden' : 'hidden'}`}
              />
              <img
                src="/assets/images/logo/logo-white.svg"
                alt="logo"
                className={`w-full ${isScrolled ? 'hidden dark:block' : 'hidden'}`}
              />
            </Link>
          </div>

          <div className="flex items-center justify-between w-full px-4">
            <div>
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="absolute right-4 top-1/2 block -translate-y-1/2 rounded-lg px-3 py-[6px] ring-primary focus:ring-2 lg:hidden"
              >
                <span className={`relative my-[6px] block h-[2px] w-[30px] ${isScrolled ? 'bg-dark dark:bg-white' : 'bg-white'}`}></span>
                <span className={`relative my-[6px] block h-[2px] w-[30px] ${isScrolled ? 'bg-dark dark:bg-white' : 'bg-white'}`}></span>
                <span className={`relative my-[6px] block h-[2px] w-[30px] ${isScrolled ? 'bg-dark dark:bg-white' : 'bg-white'}`}></span>
              </button>

              <nav className={`absolute right-4 top-full w-full max-w-[250px] rounded-lg bg-white py-5 shadow-lg dark:bg-dark-2 lg:static lg:block lg:w-full lg:max-w-full lg:bg-transparent lg:px-4 lg:py-0 lg:shadow-none dark:lg:bg-transparent xl:px-6 ${
                isMenuOpen ? 'block' : 'hidden'
              }`}>
                <ul className="block lg:flex 2xl:ml-20">
                  <li className="relative group">
                    <Link to="/" className={`flex py-2 mx-8 text-base font-medium group-hover:text-primary lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 ${
                      isScrolled ? 'text-dark dark:text-white' : 'text-white'
                    }`}>
                      Home
                    </Link>
                  </li>
                  <li className="relative group">
                    <Link to="/about" className={`flex py-2 mx-8 text-base font-medium group-hover:text-primary lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 ${
                      isScrolled ? 'text-dark dark:text-white' : 'text-white'
                    }`}>
                      About
                    </Link>
                  </li>
                  <li className="relative group">
                    <Link to="/pricing" className={`flex py-2 mx-8 text-base font-medium group-hover:text-primary lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 ${
                      isScrolled ? 'text-dark dark:text-white' : 'text-white'
                    }`}>
                      Pricing
                    </Link>
                  </li>
                  <li className="relative group">
                    <Link to="/contact" className={`flex py-2 mx-8 text-base font-medium group-hover:text-primary lg:ml-7 lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 ${
                      isScrolled ? 'text-dark dark:text-white' : 'text-white'
                    }`}>
                      Contact
                    </Link>
                  </li>
                </ul>
              </nav>
            </div>

            <div className="flex items-center justify-end pr-16 lg:pr-0">
              <button
                onClick={() => setIsDark(!isDark)}
                className="inline-flex items-center cursor-pointer mr-4"
              >
                <span className={`block ${isDark ? 'hidden' : 'block'} ${isScrolled ? 'text-dark' : 'text-white'}`}>
                  <svg className="fill-current" width="24" height="24" viewBox="0 0 24 24">
                    <path d="M13.3125 1.50001C12.675 1.31251 12.0375 1.16251 11.3625 1.05001C10.875 0.975006 10.35 1.23751 10.1625 1.68751C9.93751 2.13751 10.05 2.70001 10.425 3.00001C13.0875 5.47501 14.0625 9.11251 12.975 12.525C11.775 16.3125 8.25001 18.975 4.16251 19.0875C3.63751 19.0875 3.22501 19.425 3.07501 19.9125C2.92501 20.4 3.15001 20.925 3.56251 21.1875C4.50001 21.75 5.43751 22.2 6.37501 22.5C7.46251 22.8375 8.58751 22.9875 9.71251 22.9875C11.625 22.9875 13.5 22.5 15.1875 21.5625C17.85 20.1 19.725 17.7375 20.55 14.8875C22.1625 9.26251 18.975 3.37501 13.3125 1.50001Z"/>
                  </svg>
                </span>
                <span className={`${isDark ? 'block' : 'hidden'} ${isScrolled ? 'text-dark dark:text-white' : 'text-white'}`}>
                  <svg className="fill-current" width="24" height="24" viewBox="0 0 24 24">
                    <path d="M12 6.89999C9.18752 6.89999 6.90002 9.18749 6.90002 12C6.90002 14.8125 9.18752 17.1 12 17.1C14.8125 17.1 17.1 14.8125 17.1 12C17.1 9.18749 14.8125 6.89999 12 6.89999Z"/>
                  </svg>
                </span>
              </button>

              <div className="hidden sm:flex gap-3">
                <Link to="/signin" className={`px-6 py-2 text-base font-medium ${isScrolled ? 'text-dark dark:text-white hover:text-primary' : 'text-white hover:opacity-70'}`}>
                  Sign In
                </Link>
                <Link to="/signup" className={`px-6 py-2 text-base font-medium rounded-md transition ${isScrolled ? 'bg-primary text-white hover:bg-primary/90' : 'bg-white/20 text-white hover:bg-white hover:text-dark'}`}>
                  Sign Up
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
