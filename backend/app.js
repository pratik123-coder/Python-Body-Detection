const express = require("express");
const multer = require("multer");
const { exec } = require("child_process");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 8001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Directories for videos
const UPLOAD_DIR = path.join(__dirname, "uploads");
const PROCESSED_DIR = path.join(__dirname, "processed");

// Ensure directories exist
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);
if (!fs.existsSync(PROCESSED_DIR)) fs.mkdirSync(PROCESSED_DIR);

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => cb(null, file.originalname),
});
const upload = multer({ storage });

// Upload video
app.post("/upload", upload.single("file"), (req, res) => {
  const inputPath = path.join(UPLOAD_DIR, req.file.filename);
  const outputPath = path.join(PROCESSED_DIR, `processed_${req.file.filename}`);

  // Run the Python script for processing
  exec(
    `python3 PeopleCounter.py ${inputPath} ${outputPath}`,
    (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error.message}`);
        return res.status(500).json({ error: "Processing failed" });
      }
      if (stderr) console.error(`stderr: ${stderr}`);
      console.log(`stdout: ${stdout}`);

      res.status(200).json({ processedVideo: `/processed/${path.basename(outputPath)}` });
    }
  );
});

// Serve processed videos
app.get("/processed/:filename", (req, res) => {
  const filePath = path.join(PROCESSED_DIR, req.params.filename);
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: "File not found" });
  }
  res.sendFile(filePath);
});

// Delete uploaded and processed videos
app.delete("/delete/:filename", (req, res) => {
  const uploadFilePath = path.join(UPLOAD_DIR, req.params.filename);
  const processedFilePath = path.join(PROCESSED_DIR, `processed_${req.params.filename}`);

  // Delete both files if they exist
  if (fs.existsSync(uploadFilePath)) fs.unlinkSync(uploadFilePath);
  if (fs.existsSync(processedFilePath)) fs.unlinkSync(processedFilePath);

  res.status(200).json({ message: "Files deleted successfully" });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
