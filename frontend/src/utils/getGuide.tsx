export async function getGuide(spaceId: string) {
    console.log('Mock fetching study guide for:', spaceId);
    
    // Simulate network delay
    await new Promise((r) => setTimeout(r, 500));
  
    return {
      title: 'Photosynthesis Study Guide',
      content: `
  # Photosynthesis 🌱
  
  Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water.
  
  ## Key Points
  
  - Occurs in the chloroplast
  - Produces glucose and oxygen
  - Formula: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂
  
  ## Summary
  
  Light-dependent reactions take place in the thylakoid membranes, and the Calvin cycle occurs in the stroma.`,
    };
  }
  