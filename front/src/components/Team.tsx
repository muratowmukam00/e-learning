const Team = () => {
  const teamMembers = [
    {
      name: "Melissa Tatcher",
      position: "Marketing Expert",
      image: "/assets/images/team/team-01.png"
    },
    {
      name: "Stuard Ferrel",
      position: "Digital Marketer",
      image: "/assets/images/team/team-02.png"
    },
    {
      name: "Eva Hudson",
      position: "Creative Designer",
      image: "/assets/images/team/team-03.png"
    },
    {
      name: "Jackie Sanders",
      position: "SEO Expert",
      image: "/assets/images/team/team-04.png"
    }
  ];

  return (
    <section className="overflow-hidden bg-gray-1 pb-12 pt-20 dark:bg-dark-2 lg:pb-[90px] lg:pt-[120px]">
      <div className="container px-4 mx-auto">
        <div className="flex flex-wrap -mx-4">
          <div className="w-full px-4">
            <div className="mx-auto mb-[60px] max-w-[485px] text-center">
              <span className="block mb-2 text-lg font-semibold text-primary">Our Team Members</span>
              <h2 className="mb-3 text-3xl font-bold leading-[1.2] text-dark dark:text-white sm:text-4xl md:text-[40px]">
                Our Creative Team
              </h2>
              <p className="text-base text-body-color dark:text-dark-6">
                There are many variations of passages of Lorem Ipsum available but the majority have suffered alteration in some form.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap justify-center -mx-4">
          {teamMembers.map((member, index) => (
            <div key={index} className="w-full px-4 sm:w-1/2 lg:w-1/4 xl:w-1/4">
              <div className="px-5 pt-12 pb-10 mb-8 bg-white group rounded-xl shadow-testimonial dark:bg-dark">
                <div className="relative z-10 mx-auto mb-5 h-[120px] w-[120px]">
                  <img
                    src={member.image}
                    alt={member.name}
                    className="h-[120px] w-[120px] rounded-full"
                  />
                  <span className="absolute bottom-0 left-0 w-10 h-10 transition-all rounded-full opacity-0 -z-10 bg-secondary group-hover:opacity-100"></span>
                </div>
                <div className="text-center">
                  <h4 className="mb-1 text-lg font-semibold text-dark dark:text-white">{member.name}</h4>
                  <p className="mb-5 text-sm text-body-color dark:text-dark-6">{member.position}</p>
                  <div className="flex items-center justify-center gap-5">
                    <a href="#" className="text-dark-6 hover:text-primary">
                      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" className="fill-current">
                        <path d="M13.3315 7.25625H11.7565H11.194V6.69375V4.95V4.3875H11.7565H12.9377C13.2471 4.3875 13.5002 4.1625 13.5002 3.825V0.84375C13.5002 0.534375 13.2752 0.28125 12.9377 0.28125H10.8846C8.66272 0.28125 7.11584 1.85625 7.11584 4.19062V6.6375V7.2H6.55334H4.64084C4.24709 7.2 3.88147 7.50937 3.88147 7.95937V9.98438C3.88147 10.3781 4.19084 10.7438 4.64084 10.7438H6.49709H7.05959V11.3063V16.9594C7.05959 17.3531 7.36897 17.7188 7.81897 17.7188H10.4627C10.6315 17.7188 10.7721 17.6344 10.8846 17.5219C10.9971 17.4094 11.0815 17.2125 11.0815 17.0437V11.3344V10.7719H11.6721H12.9377C13.3033 10.7719 13.5846 10.5469 13.6408 10.2094V10.1813V10.1531L14.0346 8.2125C14.0627 8.01562 14.0346 7.79063 13.8658 7.56562C13.8096 7.425 13.5565 7.28437 13.3315 7.25625Z"/>
                      </svg>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Team;
