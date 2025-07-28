export async function getGuide(spaceId: string) {
    console.log('Mock fetching study guide for:', spaceId);
    
    // Simulate network delay
    await new Promise((r) => setTimeout(r, 500));
  
    return {
        title: 'Cloud Computing Study Guide',
        content: `
      ☁️ Cloud Computing
      
      Cloud computing is the on-demand delivery of computing services—such as servers, storage, databases, networking, software, and analytics—over the internet (“the cloud”).
      
      🔑 Key Concepts
      
      - Scalability: Resources can be scaled up or down based on demand.
      - Pay-as-you-go: Users only pay for what they use.
      - Global Accessibility: Access resources from anywhere with an internet connection.
      - Virtualization: Physical resources are abstracted into virtual environments.
      - Automation & Elasticity**: Infrastructure responds dynamically to workload changes.
      
      🏗️ Cloud Service Models
      
      - IaaS (Infrastructure as a Service): Provides virtual machines, storage, and networks (e.g., AWS EC2).
      - PaaS (Platform as a Service): Offers a development platform and environment (e.g., Google App Engine).
      - SaaS (Software as a Service): Delivers software applications over the internet (e.g., Dropbox, Salesforce).
      
      🌍 Deployment Models
      
      - Public Cloud: Services offered over the public internet.
      - Private Cloud: Cloud infrastructure operated solely for a single organization.
      - Hybrid Cloud: Combines public and private cloud features.
      - Community Cloud: Shared infrastructure for a specific community with shared concerns.
      
      🛡️ Benefits
      
      - Reduced IT costs
      - Business continuity
      - Increased collaboration
      - Flexibility and scalability
      - Automatic updates
      
      📌 Summary
      
      Cloud computing revolutionizes how businesses and individuals use technology by providing scalable, flexible, and cost-effective solutions through internet-based services. Understanding the core models and deployment types is essential for leveraging its full potential.
        `
      }      
  }
  