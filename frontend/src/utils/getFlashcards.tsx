import { Flashcard } from "../components/common/Types";

export async function getFlashcards(spaceId: string): Promise<Flashcard[]> {
    console.log('Mock fetching flashcards for:', spaceId);
  
    // Simulate delay
    await new Promise((r) => setTimeout(r, 500));
  
    return [
        {
          id: '1',
          front: 'What is Cloud Computing?',
          back: 'Cloud computing is the delivery of computing services over the internet, including storage, servers, databases, networking, and software.',
        },
        {
          id: '2',
          front: 'Name three main types of Cloud Computing services.',
          back: 'Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS).',
        },
        {
          id: '3',
          front: 'What are the deployment models of cloud computing?',
          back: 'Public cloud, private cloud, hybrid cloud, and community cloud.',
        },
        {
          id: '4',
          front: 'What is IaaS in cloud computing?',
          back: 'IaaS provides virtualized computing resources over the internet, such as virtual machines and storage.',
        },
        {
          id: '5',
          front: 'Give an example of a SaaS provider.',
          back: 'Google Workspace (formerly G Suite), which includes Gmail, Docs, Drive, and more.',
        },
        {
          id: '6',
          front: '',
          back: '',
        },
        {
          id: '7',
          front: '',
          back: '',
        },
        {
          id: '8',
          front: '',
          back: '',
        },
        {
          id: '9',
          front: '',
          back: '',
        },
        {
          id: '10',
          front: '',
          back: '',
        },
        {
          id: '11',
          front: '',
          back: '',
        },
        {
          id: '12',
          front: '',
          back: '',
        },
        {
          id: '13',
          front: '',
          back: '',
        },
        {
          id: '14',
          front: '',
          back: '',
        },
        {
          id: '15',
          front: '',
          back: '',
        },
        {
          id: '16',
          front: '',
          back: '',
        },
        {
          id: '17',
          front: '',
          back: '',
        },
        {
          id: '18',
          front: '',
          back: '',
        },
        {
          id: '19',
          front: '',
          back: '',
        },
        {
          id: '20',
          front: '',
          back: '',
        },
        {
          id: '21',
          front: '',
          back: '',
        },
        {
          id: '22',
          front: '',
          back: '',
        },
        {
          id: '23',
          front: '',
          back: '',
        },
        {
          id: '24',
          front: '',
          back: '',
        },      
    ];
  }