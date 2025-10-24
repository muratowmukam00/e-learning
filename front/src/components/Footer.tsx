import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="relative z-10 bg-[#090E34] pt-20 lg:pt-[100px]">
      <div className="container px-4 mx-auto">
        <div className="flex flex-wrap -mx-4">
          <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-4/12 xl:w-3/12">
            <div className="w-full mb-10">
              <Link to="/" className="mb-6 inline-block max-w-[160px]">
                <img src="/assets/images/logo/logo-white.svg" alt="logo" className="max-w-full" />
              </Link>
              <p className="mb-8 max-w-[270px] text-base text-gray-7">
                We create digital experiences for brands and companies by using technology.
              </p>
              <div className="flex items-center -mx-3">
                <a href="#" className="px-3 text-gray-7 hover:text-white">
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" className="fill-current">
                    <path d="M16.294 8.86875H14.369H13.6815V8.18125V6.05V5.3625H14.369H15.8128C16.1909 5.3625 16.5003 5.0875 16.5003 4.675V1.03125C16.5003 0.653125 16.2253 0.34375 15.8128 0.34375H13.3034C10.5878 0.34375 8.69714 2.26875 8.69714 5.12187V8.1125V8.8H8.00964H5.67214C5.19089 8.8 4.74402 9.17812 4.74402 9.72812V12.2031C4.74402 12.6844 5.12214 13.1313 5.67214 13.1313H7.94089H8.62839V13.8188V20.7281C8.62839 21.2094 9.00652 21.6562 9.55652 21.6562H12.7878C12.994 21.6562 13.1659 21.5531 13.3034 21.4156C13.4409 21.2781 13.544 21.0375 13.544 20.8312V13.8531V13.1656H14.2659H15.8128C16.2596 13.1656 16.6034 12.8906 16.6721 12.4781V12.4438V12.4094L17.1534 10.0375C17.1878 9.79688 17.1534 9.52187 16.9471 9.24687C16.8784 9.075 16.569 8.90312 16.294 8.86875Z"/>
                  </svg>
                </a>
                <a href="#" className="px-3 text-gray-7 hover:text-white">
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" className="fill-current">
                    <path d="M16.4647 4.83752C16.565 4.72065 16.4343 4.56793 16.2859 4.62263C15.9549 4.74474 15.6523 4.82528 15.2049 4.875C15.7552 4.56855 16.0112 4.13054 16.2194 3.59407C16.2696 3.46467 16.1182 3.34725 15.9877 3.40907C15.458 3.66023 14.8864 3.84658 14.2854 3.95668C13.6913 3.3679 12.8445 3 11.9077 3C10.1089 3 8.65027 4.35658 8.65027 6.02938C8.65027 6.26686 8.67937 6.49818 8.73427 6.71966C6.14854 6.59919 3.84286 5.49307 2.24098 3.79696C2.13119 3.68071 1.93197 3.69614 1.86361 3.83792C1.68124 4.21619 1.57957 4.63582 1.57957 5.07762C1.57957 6.12843 2.15446 7.05557 3.02837 7.59885C2.63653 7.58707 2.2618 7.51073 1.91647 7.38116C1.74834 7.31808 1.5556 7.42893 1.57819 7.59847C1.75162 8.9004 2.80568 9.97447 4.16624 10.2283C3.89302 10.2978 3.60524 10.3347 3.30754 10.3347C3.23536 10.3347 3.16381 10.3324 3.0929 10.3281C2.91247 10.3169 2.76583 10.4783 2.84319 10.6328C3.35357 11.6514 4.45563 12.3625 5.73809 12.3847C4.62337 13.1974 3.21889 13.6816 1.69269 13.6816C1.50451 13.6816 1.42378 13.9235 1.59073 14.0056C2.88015 14.6394 4.34854 15 5.90878 15C11.9005 15 15.1765 10.384 15.1765 6.38067C15.1765 6.24963 15.1732 6.11858 15.1672 5.98877C15.6535 5.66205 16.0907 5.27354 16.4647 4.83752Z"/>
                  </svg>
                </a>
                <a href="#" className="px-3 text-gray-7 hover:text-white">
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" className="fill-current">
                    <path d="M11.0297 14.4305C12.9241 14.4305 14.4598 12.8948 14.4598 11.0004C14.4598 9.10602 12.9241 7.57031 11.0297 7.57031C9.13529 7.57031 7.59958 9.10602 7.59958 11.0004C7.59958 12.8948 9.13529 14.4305 11.0297 14.4305Z"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>

          <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-2/12 xl:w-2/12">
            <div className="w-full mb-10">
              <h4 className="text-lg font-semibold text-white mb-9">About Us</h4>
              <ul>
                <li><Link to="/" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">Home</Link></li>
                <li><Link to="/about" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">About</Link></li>
                <li><Link to="/pricing" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">Pricing</Link></li>
                <li><Link to="/contact" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">Contact</Link></li>
              </ul>
            </div>
          </div>

          <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-3/12 xl:w-2/12">
            <div className="w-full mb-10">
              <h4 className="text-lg font-semibold text-white mb-9">Features</h4>
              <ul>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">How it works</a></li>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">Privacy policy</a></li>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">Terms of Service</a></li>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">Refund policy</a></li>
              </ul>
            </div>
          </div>

          <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-3/12 xl:w-2/12">
            <div className="w-full mb-10">
              <h4 className="text-lg font-semibold text-white mb-9">Our Products</h4>
              <ul>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">LineIcons</a></li>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">Ecommerce HTML</a></li>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">TailAdmin</a></li>
                <li><a href="#" className="inline-block mb-3 text-base text-gray-7 hover:text-primary">PlainAdmin</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-12 border-t border-[#8890A4]/40 py-8 lg:mt-[60px]">
        <div className="container px-4 mx-auto">
          <div className="flex flex-wrap -mx-4">
            <div className="w-full px-4 md:w-2/3 lg:w-1/2">
              <div className="my-1">
                <div className="flex items-center justify-center -mx-3 md:justify-start">
                  <a href="#" className="px-3 text-base text-gray-7 hover:text-white hover:underline">Privacy policy</a>
                  <a href="#" className="px-3 text-base text-gray-7 hover:text-white hover:underline">Legal notice</a>
                  <a href="#" className="px-3 text-base text-gray-7 hover:text-white hover:underline">Terms of service</a>
                </div>
              </div>
            </div>
            <div className="w-full px-4 md:w-1/3 lg:w-1/2">
              <div className="flex justify-center my-1 md:justify-end">
                <p className="text-base text-gray-7">
                  Designed and Developed by{' '}
                  <a href="https://tailgrids.com" target="_blank" rel="noopener noreferrer" className="text-gray-1 hover:underline">
                    TailGrids and UIdeck
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
