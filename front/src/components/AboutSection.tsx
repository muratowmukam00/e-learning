const AboutSection = () => {
  return (
    <section className="bg-gray-1 pb-8 pt-20 dark:bg-dark-2 lg:pb-[70px] lg:pt-[120px]">
      <div className="container px-4 mx-auto">
        <div className="flex flex-wrap items-center -mx-4">
          <div className="w-full px-4 lg:w-1/2">
            <div className="mb-12 max-w-[540px] lg:mb-0">
              <h2 className="mb-5 text-3xl font-bold leading-tight text-dark dark:text-white sm:text-[40px] sm:leading-[1.2]">
                Brilliant Toolkit to Build Nextgen Website Faster.
              </h2>
              <p className="mb-10 text-base leading-relaxed text-body-color dark:text-dark-6">
                The main thrust is to focus on educating attendees on how to best protect highly vulnerable business applications with interactive panel discussions and roundtables led by subject matter experts.
                <br /><br />
                The main thrust is to focus on educating attendees on how to best protect highly vulnerable business applications with interactive panel.
              </p>
              <a
                href="javascript:void(0)"
                className="inline-flex items-center justify-center py-3 text-base font-medium text-center text-white border rounded-md border-primary bg-primary px-7 hover:bg-opacity-90"
              >
                Know More
              </a>
            </div>
          </div>

          <div className="w-full px-4 lg:w-1/2">
            <div className="flex flex-wrap -mx-2 sm:-mx-4 lg:-mx-2 xl:-mx-4">
              <div className="w-full px-2 sm:w-1/2 sm:px-4 lg:px-2 xl:px-4">
                <div className="mb-4 sm:mb-8 sm:h-[400px] md:h-[540px] lg:h-[400px] xl:h-[500px]">
                  <img
                    src="/assets/images/about/about-image-01.jpg"
                    alt="about"
                    className="object-cover object-center w-full h-full"
                  />
                </div>
              </div>
              <div className="w-full px-2 sm:w-1/2 sm:px-4 lg:px-2 xl:px-4">
                <div className="mb-4 sm:mb-8 sm:h-[220px] md:h-[346px] lg:mb-4 lg:h-[225px] xl:mb-8 xl:h-[310px]">
                  <img
                    src="/assets/images/about/about-image-02.jpg"
                    alt="about"
                    className="object-cover object-center w-full h-full"
                  />
                </div>
                <div className="relative z-10 mb-4 flex items-center justify-center overflow-hidden bg-primary px-6 py-12 sm:mb-8 sm:h-[160px] sm:p-5 lg:mb-4 xl:mb-8">
                  <div>
                    <span className="block text-5xl font-extrabold text-white">09</span>
                    <span className="block text-base font-semibold text-white">We have</span>
                    <span className="block text-base font-medium text-white text-opacity-70">Years of experience</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
