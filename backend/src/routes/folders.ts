import express from 'express';
import { getFolders } from '../controllers/folderController';

const router = express.Router();

router.get('/', getFolders);

export default router;
