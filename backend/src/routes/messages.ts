import express from 'express';
import { getMessages, sendMessage } from '../controllers/messageController';

const router = express.Router();

router.get('/:spaceId/messages', getMessages);
router.post('/:spaceId/messages', sendMessage);

export default router;
