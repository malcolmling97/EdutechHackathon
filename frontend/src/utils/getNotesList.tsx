import notes from '../../tmp/notes.json';

// Mock data for notes list
export const getNotesList = async () => {
  //for testing purposes
  return Promise.resolve(notes);
}; 