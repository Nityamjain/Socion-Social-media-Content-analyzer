document.addEventListener("DOMContentLoaded", () => {
  const dropArea = document.getElementById("drop-area");
  const fileInput = document.getElementById("file-upload");
  const fileNameText = document.getElementById("selected-file-name");
  const previewImg = document.getElementById("file-preview");
  const uploadForm = document.getElementById("uploadForm");
  const analyzeBtn = document.getElementById("analyzeBtn");

  // Modal
  const modal = document.getElementById("analysis-modal");
  const modalFilename = document.getElementById("modal-filename");
  const processStep = document.getElementById("process-step");
  const progressBar = document.getElementById("progress-bar-inner");

  let selectedFile = null;

  // -----------------------------
  // HANDLE FILE SELECTION
  // -----------------------------
  function handleFile() {
    selectedFile = fileInput.files[0];

    if (!selectedFile) {
      fileNameText.textContent = "No file selected";
      previewImg.style.display = "none";
      return;
    }
    dropArea.classList.add("file-selected");

    fileNameText.textContent = selectedFile.name;

    if (selectedFile.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = e => {
        previewImg.src = e.target.result;
        previewImg.style.display = "block";
      };
      reader.readAsDataURL(selectedFile);
    } else {
      previewImg.style.display = "none";
    }
  }

  fileInput.addEventListener("change", handleFile);


  // -----------------------------
  // DRAG & DROP
  // -----------------------------
  dropArea.addEventListener("dragover", e => {
    e.preventDefault();
    dropArea.classList.add("drag-over");
  });

  dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("drag-over");
  });

  dropArea.addEventListener("drop", e => {
    e.preventDefault();
    dropArea.classList.remove("drag-over");
    fileInput.files = e.dataTransfer.files;
    handleFile();
  });


  // -----------------------------
  // CLICK "ANALYZE"
  // -----------------------------
  analyzeBtn.addEventListener("click", async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      alert("Please upload a file first.");
      return;
    }

    // Show modal
    modal.style.display = "flex";
    modalFilename.textContent = selectedFile.name;
    progressBar.style.width = "0%";

    // -----------------------------
    // 1️⃣ Upload file first to /upload
    // -----------------------------
    processStep.textContent = "Uploading file...";

    const formData = new FormData();
    formData.append("file", selectedFile);

    const uploadRes = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    const uploadData = await uploadRes.json();
    const task_id = uploadData.task_id;

    if (!task_id) {
      alert("Upload failed.");
      return;
    }

    // Fake initial progress
    await smoothProgressTo(30);

    // -----------------------------
    // 2️⃣ Start SSE stream from /analyze_stream/<task_id>
    // -----------------------------
    processStep.textContent = "Processing...";

    const eventSource = new EventSource(`/analyze_stream/${task_id}`);

   eventSource.addEventListener("progress", (e) => {
    const data = JSON.parse(e.data);
    processStep.textContent = data.step;
    incrementProgress(data.progress);
});

    eventSource.addEventListener("result", (e) => {
      const result = JSON.parse(e.data);
      console.log("FINAL RESULT:", result);

      progressBar.style.width = "100%";
      processStep.textContent = "Complete!";

      setTimeout(() => {
        modal.style.display = "none";

        // Store result for dashboard if needed
        localStorage.setItem("analysis_result", e.data);

        // Redirect
        const reader = new FileReader();
          reader.onload = (e) => {
            localStorage.setItem('post_image_data', e.target.result);
          };
          reader.readAsDataURL(selectedFile);
        window.location.href = "/dashboard";
      }, 800);
    });

    eventSource.addEventListener("error", (e) => {
      console.error("Stream error:", e);
      processStep.textContent = "Error occurred!";
      eventSource.close();
    });
  });


  // -----------------------------
  // PROGRESS HELPERS
  // -----------------------------
  function incrementProgress(amount) {
    let current = parseInt(progressBar.style.width) || 0;
    let next = Math.min(current + amount,100);
    progressBar.style.width = next + "%";
  }

  function smoothProgressTo(target) {
    return new Promise(resolve => {
      let current = parseInt(progressBar.style.width) || 0;

      const timer = setInterval(() => {
        if (current >= target) {
          clearInterval(timer);
          resolve();
          return;
        }
        current++;
        progressBar.style.width = current + "%";
      }, 20);
    });
  }
});
