import UIKit
import AVFoundation
import Vision

protocol CameraViewControllerDelegate: AnyObject {
    func didCaptureImage(_ image: UIImage)
}

class CameraViewController: UIViewController, AVCaptureVideoDataOutputSampleBufferDelegate, AVCapturePhotoCaptureDelegate {
    
    weak var delegate: CameraViewControllerDelegate?
    
    private var captureSession: AVCaptureSession!
    private var previewLayer: AVCaptureVideoPreviewLayer!
    private var photoOutput: AVCapturePhotoOutput!
    
    // UI Overlays
    private var overlayLayer: CAShapeLayer!
    private var feedbackLabel: UILabel!
    
    // Vision
    private var visionRequests = [VNRequest]()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
        setupOverlay()
        setupVision()
    }
    
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        previewLayer.frame = view.bounds
        overlayLayer.frame = view.bounds
    }
    
    // MARK: - Setup
    
    private func setupCamera() {
        captureSession = AVCaptureSession()
        captureSession.sessionPreset = .high
        
        guard let videoCaptureDevice = AVCaptureDevice.default(for: .video) else { return }
        let videoInput: AVCaptureDeviceInput
        
        do {
            videoInput = try AVCaptureDeviceInput(device: videoCaptureDevice)
        } catch {
            return
        }
        
        if (captureSession.canAddInput(videoInput)) {
            captureSession.addInput(videoInput)
        }
        
        // Video Preview
        previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        previewLayer.videoGravity = .resizeAspectFill
        view.layer.addSublayer(previewLayer)
        
        // Vision Data Output
        let videoOutput = AVCaptureVideoDataOutput()
        videoOutput.setSampleBufferDelegate(self, queue: DispatchQueue(label: "videoQueue"))
        if (captureSession.canAddOutput(videoOutput)) {
            captureSession.addOutput(videoOutput)
        }
        
        // Photo Output (Final Capture)
        photoOutput = AVCapturePhotoOutput()
        if (captureSession.canAddOutput(photoOutput)) {
            captureSession.addOutput(photoOutput)
        }
        
        captureSession.startRunning()
    }
    
    private func setupOverlay() {
        // Redrawable layer for boxes
        overlayLayer = CAShapeLayer()
        overlayLayer.fillColor = UIColor.clear.cgColor
        overlayLayer.strokeColor = UIColor.yellow.cgColor
        overlayLayer.lineWidth = 3
        view.layer.addSublayer(overlayLayer)
        
        // Feedback Text
        feedbackLabel = UILabel()
        feedbackLabel.translatesAutoresizingMaskIntoConstraints = false
        feedbackLabel.textAlignment = .center
        feedbackLabel.textColor = .yellow
        feedbackLabel.backgroundColor = UIColor.black.withAlphaComponent(0.6)
        feedbackLabel.font = UIFont.boldSystemFont(ofSize: 18)
        feedbackLabel.text = "Søker etter postkasser..."
        feedbackLabel.layer.cornerRadius = 8
        feedbackLabel.clipsToBounds = true
        view.addSubview(feedbackLabel)
        
        NSLayoutConstraint.activate([
            feedbackLabel.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            feedbackLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            // FIX: Use leadingAnchor instead of non-existent paddingAnchor
            feedbackLabel.leadingAnchor.constraint(greaterThanOrEqualTo: view.leadingAnchor, constant: 20)
        ])
        
        // Fix constraint simplisticly
        feedbackLabel.widthAnchor.constraint(greaterThanOrEqualToConstant: 200).isActive = true
        feedbackLabel.heightAnchor.constraint(equalToConstant: 40).isActive = true
    }
    
    private func setupVision() {
        let rectangleDetectionRequest = VNDetectRectanglesRequest(completionHandler: self.handleRectangles)
        rectangleDetectionRequest.minimumConfidence = 0.5
        rectangleDetectionRequest.minimumSize = 0.1 // Min 10% of screen
        rectangleDetectionRequest.maximumObservations = 20
        self.visionRequests = [rectangleDetectionRequest]
    }
    
    // MARK: - Actions
    
    func capturePhoto() {
        let settings = AVCapturePhotoSettings()
        photoOutput.capturePhoto(with: settings, delegate: self)
    }
    
    // MARK: - Vision Logic
    
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let imageRequestHandler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .up, options: [:])
        do {
            try imageRequestHandler.perform(self.visionRequests)
        } catch {
            print(error)
        }
    }
    
    private func handleRectangles(request: VNRequest, error: Error?) {
        guard let results = request.results as? [VNRectangleObservation] else { return }
        
        DispatchQueue.main.async { [weak self] in
            self?.drawRectangles(results)
            self?.updateFeedback(results)
        }
    }
    
    private func drawRectangles(_ rectangles: [VNRectangleObservation]) {
        let path = UIBezierPath()
        
        // Remove old text layers (simple clean-up)
        overlayLayer.sublayers?.filter { $0 is CATextLayer }.forEach { $0.removeFromSuperlayer() }
        
        for rect in rectangles {
            // VNRectangleObservation returns coords 0-1 (normalized).
            // Y-axis is flipped in Vision compared to UIKit.
            let convertedRect = previewLayer.layerRectConverted(fromMetadataOutputRect: CGRect(x: rect.boundingBox.origin.x, y: 1 - rect.boundingBox.origin.y - rect.boundingBox.height, width: rect.boundingBox.width, height: rect.boundingBox.height))
            
            path.append(UIBezierPath(rect: convertedRect))
            
            // MEASUREMENT LOGIC
            let referenceWidthCM: CGFloat = 40.0
            
            // Calculate est. width
            let pixelWidth = convertedRect.width
            let screenWidth = previewLayer.bounds.width
            let widthRatio = pixelWidth / screenWidth
            
            let estimatedWidthCM = widthRatio * referenceWidthCM
            let estimatedHeightCM = estimatedWidthCM * (convertedRect.height / convertedRect.width)
            
            // Create Label
            let textLayer = CATextLayer()
            textLayer.string = String(format: "W: %.1f cm\nH: %.1f cm", estimatedWidthCM, estimatedHeightCM)
            textLayer.fontSize = 14
            textLayer.foregroundColor = UIColor.yellow.cgColor
            textLayer.backgroundColor = UIColor.black.withAlphaComponent(0.6).cgColor
            textLayer.cornerRadius = 4
            textLayer.alignmentMode = .center
            textLayer.contentsScale = UIScreen.main.scale
            
            // Position Label above the box
            let labelWidth: CGFloat = 80
            let labelHeight: CGFloat = 36
            textLayer.frame = CGRect(x: convertedRect.midX - (labelWidth / 2), y: convertedRect.minY - labelHeight - 5, width: labelWidth, height: labelHeight)
            
            overlayLayer.addSublayer(textLayer)
        }
        
        overlayLayer.path = path.cgPath
    }
    
    private func updateFeedback(_ rectangles: [VNRectangleObservation]) {
        if rectangles.isEmpty {
            feedbackLabel.text = "Ingen postkasser funnet"
            feedbackLabel.textColor = .orange
            overlayLayer.strokeColor = UIColor.orange.cgColor
        } else {
            // Check size to give "Move Closer" hints
            // Using logic: if largest rect height < 0.15 (15% of screen), suggest moving closer.
            if let maxRect = rectangles.max(by: { $0.boundingBox.height < $1.boundingBox.height }) {
                if maxRect.boundingBox.height < 0.15 {
                    feedbackLabel.text = "Gå nærmere"
                    feedbackLabel.textColor = .yellow
                    overlayLayer.strokeColor = UIColor.yellow.cgColor
                } else {
                    feedbackLabel.text = "Postkasse funnet! (Ta bilde)"
                    feedbackLabel.textColor = .green
                    overlayLayer.strokeColor = UIColor.green.cgColor
                }
            }
        }
    }
    
    // MARK: - Photo Capture Delegate
    
    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        guard let imageData = photo.fileDataRepresentation(),
              let image = UIImage(data: imageData) else { return }
        
        // Stop camera
        captureSession.stopRunning()
        delegate?.didCaptureImage(image)
    }
}
