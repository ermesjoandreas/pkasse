import SwiftUI
import UIKit

// Shared helper to trigger capture from SwiftUI
class ARCameraCoordinatorHolder: ObservableObject {
    var triggerAction: (() -> Void)?
}

// ... resten av ARCameraView koden er under her ...


struct ARCameraView: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Binding var isPresented: Bool
    @ObservedObject var coordinatorHolder: ARCameraCoordinatorHolder
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    func makeUIViewController(context: Context) -> CameraViewController {
        let controller = CameraViewController()
        controller.delegate = context.coordinator
        context.coordinator.controller = controller
        
        // Bind the trigger action so SwiftUI button can call it
        coordinatorHolder.triggerAction = { [weak controller] in
            controller?.capturePhoto()
        }
        
        return controller
    }
    
    func updateUIViewController(_ uiViewController: CameraViewController, context: Context) {
        // Updates can go here
    }
    
    class Coordinator: NSObject, CameraViewControllerDelegate {
        var parent: ARCameraView
        var controller: CameraViewController?
        
        init(_ parent: ARCameraView) {
            self.parent = parent
        }
        
        func didCaptureImage(_ image: UIImage) {
            parent.image = image
            parent.isPresented = false
        }
    }
}
