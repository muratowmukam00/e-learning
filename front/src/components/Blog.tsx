const Blog = () => {
  const blogs = [
    {
      date: "Dec 22, 2023",
      title: "Meet AutoManage, the best AI management tools",
      description: "Lorem Ipsum is simply dummy text of the printing and typesetting industry.",
      image: "/assets/images/blog/blog-01.jpg"
    },
    {
      date: "Mar 15, 2023",
      title: "How to earn more money as a wellness coach",
      description: "Lorem Ipsum is simply dummy text of the printing and typesetting industry.",
      image: "/assets/images/blog/blog-02.jpg"
    },
    {
      date: "Jan 05, 2023",
      title: "The no-fuss guide to upselling and cross selling",
      description: "Lorem Ipsum is simply dummy text of the printing and typesetting industry.",
      image: "/assets/images/blog/blog-03.jpg"
    }
  ];

  return (
    <section className="bg-white pb-10 pt-20 dark:bg-dark lg:pb-20 lg:pt-[120px]">
      <div className="container px-4 mx-auto">
        <div className="flex flex-wrap justify-center -mx-4">
          <div className="w-full px-4">
            <div className="mx-auto mb-[60px] max-w-[485px] text-center">
              <span className="block mb-2 text-lg font-semibold text-primary">Our Blogs</span>
              <h2 className="mb-4 text-3xl font-bold text-dark dark:text-white sm:text-4xl md:text-[40px] md:leading-[1.2]">
                Our Recent News
              </h2>
              <p className="text-base text-body-color dark:text-dark-6">
                There are many variations of passages of Lorem Ipsum available but the majority have suffered alteration in some form.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap -mx-4">
          {blogs.map((blog, index) => (
            <div key={index} className="w-full px-4 md:w-1/2 lg:w-1/3">
              <div className="mb-10 group">
                <div className="mb-8 overflow-hidden rounded-[5px]">
                  <a href="#" className="block">
                    <img
                      src={blog.image}
                      alt="blog"
                      className="w-full transition group-hover:rotate-6 group-hover:scale-125"
                    />
                  </a>
                </div>
                <div>
                  <span className="mb-6 inline-block rounded-[5px] bg-primary px-4 py-0.5 text-center text-xs font-medium leading-loose text-white">
                    {blog.date}
                  </span>
                  <h3>
                    <a
                      href="#"
                      className="inline-block mb-4 text-xl font-semibold text-dark hover:text-primary dark:text-white dark:hover:text-primary sm:text-2xl lg:text-xl xl:text-2xl"
                    >
                      {blog.title}
                    </a>
                  </h3>
                  <p className="max-w-[370px] text-base text-body-color dark:text-dark-6">
                    {blog.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Blog;
