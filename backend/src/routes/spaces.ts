import express from 'express';
import { getSpaces, createSpace } from '../controllers/spaceController';

const router = express.Router();

router.get('/:folderId/spaces', getSpaces);
router.post('/:folderId/spaces', createSpace);

export default router;
