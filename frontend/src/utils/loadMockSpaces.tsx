// utils/preloadMockSpaces.ts
export const loadMockSpaces = async () => {
    const existing = JSON.parse(localStorage.getItem('chat-list') || '[]');
    if (existing.length > 0) return;
  
    const res = await fetch('/mock_spaces_with_generatedTypes.json');
    const data = await res.json();
    localStorage.setItem('chat-list', JSON.stringify(data));
    window.dispatchEvent(new CustomEvent('spaces-added'));
  };
  