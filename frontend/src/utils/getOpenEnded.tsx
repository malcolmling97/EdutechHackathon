export async function getOpenEndedQuestion(spaceId: string) {
    console.log('Mock fetching open-ended question for:', spaceId);
  
    await new Promise((r) => setTimeout(r, 300));
  
    return {
      id: 'q1',
      prompt: `How would you build your 6-Pokémon team where synergies are banned? Explain your choices based on synergy, type coverage, roles (tank, sweeper, support, etc.), and any specific strategies you would use to win.`,
      explanation: 'There no right or wrong answer, just show your thinking process.',
    };
  }
  