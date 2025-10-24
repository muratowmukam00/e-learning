import { useState } from 'react';

const Testimonials = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const testimonials = [
    {
      rating: 5,
      text: "Our members are so impressed. It's intuitive. It's clean. It's distraction free. If you're building a community.",
      author: "Sabo Masties",
      position: "Founder @ Rolex",
      image: "/assets/images/testimonials/author-01.jpg"
    },
    {
      rating: 5,
      text: "Our members are so impressed. It's intuitive. It's clean. It's distraction free. If you're building a community.",
      author: "Musharof Chowdhury",
      position: "Founder @ Ayro UI",
      image: "/assets/images/testimonials/author-02.jpg"
    },
    {
      rating: 5,
      text: "Our members are so impressed. It's intuitive. It's clean. It's distraction free. If you're building a community.",
      author: "William Smith",
      position: "Founder @ Trorex",
      image: "/assets/images/testimonials/author-03.jpg"
    }
  ];

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % testimonials.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  return (
    <section className="overflow-hidden bg-gray-1 py-20 dark:bg-dark-2 md:py-[120px]">
      <div className="container px-4 mx-auto">
        <div className="flex flex-wrap justify-center -mx-4">
          <div className="w-full px-4">
            <div className="mx-auto mb-[60px] max-w-[485px] text-center">
              <span className="block mb-2 text-lg font-semibold text-primary">Testimonials</span>
              <h2 className="mb-3 text-3xl font-bold leading-[1.2] text-dark dark:text-white sm:text-4xl md:text-[40px]">
                What our Clients Say
              </h2>
              <p className="text-base text-body-color dark:text-dark-6">
                There are many variations of passages of Lorem Ipsum available but the majority have suffered alteration in some form.
              </p>
            </div>
          </div>
        </div>

        <div className="relative">
          <div className="overflow-hidden">
            <div className="flex transition-transform duration-500 ease-in-out" style={{ transform: `translateX(-${currentSlide * 100}%)` }}>
              {testimonials.map((testimonial, index) => (
                <div key={index} className="w-full flex-shrink-0 px-4">
                  <div className="rounded-xl bg-white px-4 py-[30px] shadow-testimonial dark:bg-dark sm:px-[30px]">
                    <div className="mb-[18px] flex items-center gap-[2px]">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <svg key={i} width="20" height="20" viewBox="0 0 20 20" fill="none">
                          <path d="M10 0L12.2451 6.90983H19.5106L13.6327 11.1803L15.8779 18.0902L10 13.8197L4.12215 18.0902L6.36729 11.1803L0.489435 6.90983H7.75486L10 0Z" fill="#FFB800"/>
                        </svg>
                      ))}
                    </div>
                    <p className="mb-6 text-base text-body-color dark:text-dark-6">
                      {testimonial.text}
                    </p>
                    <div className="flex items-center gap-4">
                      <div className="h-[50px] w-[50px] overflow-hidden rounded-full">
                        <img src={testimonial.image} alt={testimonial.author} className="h-full w-full object-cover" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-dark dark:text-white">{testimonial.author}</h3>
                        <p className="text-xs text-body-secondary">{testimonial.position}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-[60px] flex items-center justify-center gap-4">
            <button
              onClick={prevSlide}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-primary shadow-md hover:bg-primary hover:text-white dark:bg-dark-2"
            >
              <svg className="fill-current" width="22" height="22" viewBox="0 0 22 22">
                <path d="M19.25 10.2437H4.57187L10.4156 4.29687C10.725 3.9875 10.725 3.50625 10.4156 3.19687C10.1062 2.8875 9.625 2.8875 9.31562 3.19687L2.2 10.4156C1.89062 10.725 1.89062 11.2063 2.2 11.5156L9.31562 18.7344C9.45312 18.8719 9.65937 18.975 9.86562 18.975C10.0719 18.975 10.2437 18.9062 10.4156 18.7687C10.725 18.4594 10.725 17.9781 10.4156 17.6688L4.60625 11.7906H19.25C19.6625 11.7906 20.0063 11.4469 20.0063 11.0344C20.0063 10.5875 19.6625 10.2437 19.25 10.2437Z"/>
              </svg>
            </button>
            <button
              onClick={nextSlide}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-primary shadow-md hover:bg-primary hover:text-white dark:bg-dark-2"
            >
              <svg className="fill-current" width="22" height="22" viewBox="0 0 22 22">
                <path d="M19.8 10.45L12.6844 3.2313C12.375 2.92192 11.8938 2.92192 11.5844 3.2313C11.275 3.54067 11.275 4.02192 11.5844 4.3313L17.3594 10.2094H2.75C2.3375 10.2094 1.99375 10.5532 1.99375 10.9657C1.99375 11.3782 2.3375 11.7563 2.75 11.7563H17.4281L11.5844 17.7032C11.275 18.0126 11.275 18.4938 11.5844 18.8032C11.7219 18.9407 11.9281 19.0094 12.1344 19.0094C12.3406 19.0094 12.5469 18.9407 12.6844 18.7688L19.8 11.55C20.1094 11.2407 20.1094 10.7594 19.8 10.45Z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
