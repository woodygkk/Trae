document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const bgHeightInput = document.getElementById('bg-height');
    const fontSizeInput = document.getElementById('font-size');
    const fontColorInput = document.getElementById('font-color');
    const strokeColorInput = document.getElementById('stroke-color');
    const subtitleTextarea = document.getElementById('subtitle-text');
    const generateBtn = document.getElementById('generate-btn');
    const saveBtn = document.getElementById('save-btn');
    const canvas = document.getElementById('preview-canvas');
    const ctx = canvas.getContext('2d');

    let baseImage = null;

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        fileName.textContent = file.name;
        const reader = new FileReader();
        reader.onload = () => {
            const img = new Image();
            img.onload = () => {
                baseImage = img;
                resizeCanvasToImage(img);
                draw();
            };
            img.src = reader.result;
        };
        reader.readAsDataURL(file);
    });

    generateBtn.addEventListener('click', draw);

    [bgHeightInput, fontSizeInput, fontColorInput, strokeColorInput, subtitleTextarea]
        .forEach(el => el.addEventListener('input', debounce(draw, 200)));

    saveBtn.addEventListener('click', () => {
        if (!canvas.width || !canvas.height) return;
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated_image.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    function resizeCanvasToImage(img) {
        const maxWidth = 1000;
        const scale = img.width > maxWidth ? maxWidth / img.width : 1;
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
    }

    function draw() {
        if (!baseImage) {
            clearCanvas();
            return;
        }

        const lines = subtitleTextarea.value
            .split(/\r?\n/)
            .map(s => s.trim())
            .filter(s => s.length > 0);

        const bgHeight = clamp(parseInt(bgHeightInput.value || '40', 10), 10, 300);
        const fontSize = clamp(parseInt(fontSizeInput.value || '20', 10), 10, 120);
        const fontColor = fontColorInput.value || '#FFFFFF';
        const strokeColor = strokeColorInput.value || '#000000';

        fitCanvasToImage(baseImage);

        ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);

        const totalHeight = bgHeight * lines.length;
        const startY = canvas.height - totalHeight;

        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = `${fontSize}px Arial, Helvetica, sans-serif`;

        lines.forEach((text, index) => {
            const yTop = startY + index * bgHeight;
            ctx.fillStyle = 'rgba(0,0,0,0.6)';
            ctx.fillRect(0, yTop, canvas.width, bgHeight);

            ctx.strokeStyle = 'rgba(255,255,255,0.25)';
            ctx.lineWidth = 1;
            if (index > 0) ctx.beginPath(), ctx.moveTo(0, yTop), ctx.lineTo(canvas.width, yTop), ctx.stroke();

            if (index < lines.length - 1) {
                const yBottom = yTop + bgHeight;
                ctx.beginPath();
                ctx.moveTo(0, yBottom);
                ctx.lineTo(canvas.width, yBottom);
                ctx.stroke();
            }

            const textY = yTop + bgHeight / 2;
            ctx.lineWidth = Math.max(1, Math.round(fontSize / 12));
            ctx.strokeStyle = strokeColor;
            ctx.fillStyle = fontColor;
            ctx.strokeText(text, canvas.width / 2, textY);
            ctx.fillText(text, canvas.width / 2, textY);
        });
    }

    function fitCanvasToImage(img) {
        if (canvas.width === img.width && canvas.height === img.height) return;
        const maxWidth = 1000;
        const scale = img.width > maxWidth ? maxWidth / img.width : 1;
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
    }

    function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    function clamp(v, min, max) {
        return Math.min(max, Math.max(min, v));
    }

    function debounce(fn, wait) {
        let t;
        return function () {
            clearTimeout(t);
            t = setTimeout(fn, wait);
        };
    }
});
