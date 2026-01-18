//
//  AnalysisResponse.swift
//  pkasse
//
//  Created by Andreas Ermesjø on 18/01/2026.
//


import Foundation

struct AnalysisResponse: Codable {
    let success: Bool
    let postkasser: [PostkasseResult]
    let count: Int
}

struct PostkasseResult: Codable, Identifiable {
    var id: String { postkasseID } // Map 'id' from JSON to identifiable property
    let postkasseID: String
    let kapasitetKlasse: String
    
    enum CodingKeys: String, CodingKey {
        case postkasseID = "id"
        case kapasitetKlasse = "kapasitet_klasse"
    }
}
