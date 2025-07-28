export async function getOpenEndedQuestion(spaceId: string) {
    console.log('Mock fetching open-ended question for:', spaceId);
  
    await new Promise((r) => setTimeout(r, 300));
  
    return [
      {
        id: 'q1',
        prompt: `Imagine your company wants to scale globally but has limited infrastructure. How would you use cloud computing to support this goal? Explain your strategy and the benefits you expect to gain.`,
        explanation: 'This question tests your understanding of cloud scalability, global availability, and business alignment.',
      },
      {
        id: 'q2',
        prompt: `You're designing a web application that must handle unpredictable spikes in user traffic. How would cloud computing help you address this challenge?`,
        explanation: 'Look for answers that mention elasticity, autoscaling, and load balancing.',
      },
      {
        id: 'q3',
        prompt: `Compare and contrast IaaS, PaaS, and SaaS. When would you use each model and why?`,
        explanation: 'This encourages explanation of use cases and understanding of cloud service models.',
      },
      {
        id: 'q4',
        prompt: `A company is hesitant to migrate to the cloud due to security concerns. How would you address these concerns and ensure their data remains safe?`,
        explanation: 'Answers should reflect cloud security practices like encryption, IAM, compliance, and shared responsibility.',
      },
      {
        id: 'q5',
        prompt: `You’re tasked with building a development environment for a remote team. What cloud tools or services would you include and why?`,
        explanation: 'This checks familiarity with developer tools, version control, CI/CD, and cloud collaboration solutions.',
      }
    ];
  }
  