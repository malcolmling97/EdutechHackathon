import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getGuide } from '../utils/getGuide';

const StudyGuideView = () => {
  const { spaceId = 'mock-space-id' } = useParams();
  const [guide, setGuide] = useState<{ title: string; content: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGuide(spaceId)
      .then((data) => setGuide(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [spaceId]);

  return (
    <div className="p-6 max-w-4xl mx-auto text-white">
      {loading ? (
        <p className="text-gray-400">Loading study guide...</p>
      ) : (
        <>
          <h1 className="text-2xl font-bold mb-4">{guide?.title}</h1>
          <pre className="whitespace-pre-wrap bg-gray-800 p-4 rounded-md">{guide?.content}</pre>
        </>
      )}
    </div>
  );
};

export default StudyGuideView;
