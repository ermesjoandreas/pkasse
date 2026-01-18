import Foundation
import UIKit

class NetworkManager: ObservableObject {
    // IMPORTANT: Replace with your Mac's Local IP Address!
    // Simulator runs on Mac so "localhost" works, but for physical device use local IP.
    @Published var serverURL = "http://localhost:5000/analyze"
    
    func uploadImage(image: UIImage) async throws -> [PostkasseResult] {
        guard let url = URL(string: serverURL) else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            throw URLError(.cannotDecodeContentData)
        }
        
        let body = createBody(boundary: boundary, data: imageData, mimeType: "image/jpeg", filename: "upload.jpg")
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        
        let decodedResponse = try JSONDecoder().decode(AnalysisResponse.self, from: data)
        return decodedResponse.postkasser
    }
    
    private func createBody(boundary: String, data: Data, mimeType: String, filename: String) -> Data {
        var body = Data()
        let lineBreak = "\r\n"
        
        body.append("--\(boundary + lineBreak)")
        body.append("Content-Disposition: form-data; name=\"image\"; filename=\"\(filename)\"\(lineBreak)")
        body.append("Content-Type: \(mimeType + lineBreak + lineBreak)")
        body.append(data)
        body.append(lineBreak)
        body.append("--\(boundary)--\(lineBreak)")
        
        return body
    }
}

extension Data {
    mutating func append(_ string: String) {
        if let data = string.data(using: .utf8) {
            append(data)
        }
    }
}
