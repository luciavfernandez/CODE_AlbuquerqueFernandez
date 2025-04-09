"""
File N°2: syntethic_data.py

This file is crutial for our loading data into Neo4j. The idea is to complete the data from and merge with syntethic data. 

Additionally, it is important that the papers are coming from dblp.org, they have similar keywords, conferences, journals, and workshops 
in order to create the relationships in the platform.

"""

import random
import re

keyword_list = [
    "Algorithm",
    "Data Structure",
    "Machine Learning",
    "Artificial Intelligence",
    "Data Querying",
    "Data Storage",
    "Database",
    "Data Processing",
    "Networking",
    "Operating System",
    "Software Development",
    "Programming",
    "Compiler",
    "Data Management",
    "Big Data",
    "Cloud Storage",
    "Virtualization",
    "Indexing",
    "Automation",
    "Data Modeling"
]

conferences = [
    {"id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9", "name": "European Conference on Artificial Intelligence", "edition": 30, "city": "Vienna"},
    {"id": "b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7t8u0", "name": "International Conference on Computer Vision", "edition": 24, "city": "Paris"},
    {"id": "c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6t7v8w1", "name": "European Symposium on Algorithms", "edition": 22, "city": "Berlin"},
    {"id": "d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5t6u7w8x2", "name": "International Conference on Machine Learning", "edition": 40, "city": "Stockholm"},
    {"id": "e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6v7w8y3", "name": "European Conference on Computer Vision", "edition": 28, "city": "Zurich"},
    {"id": "f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8z4", "name": "ACM SIGPLAN Symposium on Principles of Programming Languages", "edition": 45, "city": "Rome"},
    {"id": "g1h2i3j4k5l6m7n8o9p0q1r2s3t4u5v6w7x8a5", "name": "European Conference on Data Mining", "edition": 12, "city": "London"},
    {"id": "h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y9b6", "name": "International Conference on Software Engineering", "edition": 35, "city": "Madrid"},
    {"id": "i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z0c7", "name": "International Conference on High Performance Computing", "edition": 15, "city": "Copenhagen"},
    {"id": "j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8d8", "name": "European Workshop on Computational Biology", "edition": 18, "city": "Paris"},
    {"id": "k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b9e9", "name": "International Conference on Neural Information Processing", "edition": 50, "city": "Barcelona"},
    {"id": "l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c0f0", "name": "International Conference on Computational Intelligence", "edition": 60, "city": "Frankfurt"},
    {"id": "m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c8d1g1", "name": "European Conference on Quantum Computing", "edition": 7, "city": "Lisbon"},
    {"id": "n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d9e2h2", "name": "International Conference on Computational Science", "edition": 20, "city": "Athens"},
    {"id": "o1p2q3r4s5t6u7v8w9x0y1z2a3b4c5d0e3f3i3", "name": "European Conference on Network and Communications", "edition": 16, "city": "Brussels"},
    {"id": "p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e1f4g4j4", "name": "International Conference on Algorithms and Architectures", "edition": 11, "city": "Rome"},
    {"id": "q1r2s3t4u5v6w7x8y9z0a1b2c3d4e5f5g6h5k5", "name": "International Conference on Internet of Things", "edition": 25, "city": "Berlin"},
    {"id": "r1s2t3u4v5w6x7y8z9a0b1c2d3e4f6g7h8i0l6", "name": "ACM Conference on Computing Frontiers", "edition": 27, "city": "Milan"},
    {"id": "s1t2u3v4w5x6y7z8a9b0c1d2e3f4g8h9i1j1m7", "name": "European Conference on Human-Computer Interaction", "edition": 41, "city": "Stockholm"}
]

journals = [
    {"id": "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s", "name": "Journal of Computer Science and Technology", "edition": 52, "city": "Berlin"},
    {"id": "2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0t", "name": "Computer Science Review", "edition": 40, "city": "London"},
    {"id": "3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1u", "name": "Journal of Artificial Intelligence Research", "edition": 18, "city": "Paris"},
    {"id": "4a5b6c7d8e9f0g1h2i3j4k5l6m7n8o9p0q1r2v", "name": "International Journal of Computer Vision", "edition": 60, "city": "Zurich"},
    {"id": "5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3w", "name": "Theoretical Computer Science", "edition": 22, "city": "Vienna"},
    {"id": "6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4x", "name": "Journal of Machine Learning Research", "edition": 34, "city": "Amsterdam"},
    {"id": "7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5y", "name": "Journal of Computational and Graphical Statistics", "edition": 25, "city": "Rome"},
    {"id": "8a9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6z", "name": "Software: Practice and Experience", "edition": 10, "city": "Milan"},
    {"id": "9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7a", "name": "ACM Transactions on Computer Systems", "edition": 44, "city": "Stockholm"},
    {"id": "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8b", "name": "IEEE Transactions on Computers", "edition": 55, "city": "Helsinki"},
    {"id": "1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9c", "name": "Journal of the ACM", "edition": 12, "city": "Copenhagen"},
    {"id": "2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9t0d", "name": "Computers in Biology and Medicine", "edition": 11, "city": "Barcelona"},
    {"id": "3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0u1e", "name": "Information and Computation", "edition": 20, "city": "Lisbon"},
    {"id": "4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1v2f", "name": "International Journal of Computer Applications", "edition": 36, "city": "Geneva"},
    {"id": "5b6c7d8e9f0g1h2i3j4k5l6m7n8o9p0q1r2w3g", "name": "Computer Networks", "edition": 49, "city": "Madrid"},
    {"id": "6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3y4h", "name": "Computers & Security", "edition": 63, "city": "Oslo"},
    {"id": "7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4z5i", "name": "Information Processing Letters", "edition": 27, "city": "Paris"},
    {"id": "8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5x6j", "name": "Journal of Logic and Algebraic Programming", "edition": 17, "city": "Frankfurt"},
    {"id": "9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6y7k", "name": "Science of Computer Programming", "edition": 30, "city": "Vienna"},
    {"id": "0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7z8l", "name": "Journal of Network and Computer Applications", "edition": 58, "city": "Brussels"}
]

workshops = [
    {"id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s1", "name": "Workshop on Artificial Intelligence", "edition": 14, "city": "Vienna"},
    {"id": "b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7t8u2", "name": "Workshop on Machine Learning and Data Science", "edition": 9, "city": "Berlin"},
    {"id": "c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6t7v8w3", "name": "Workshop on Computer Vision", "edition": 12, "city": "Paris"},
    {"id": "d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5t6u7w8x4", "name": "Workshop on Computational Biology", "edition": 5, "city": "Rome"},
    {"id": "e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6v7w8y5", "name": "Workshop on Quantum Computing", "edition": 3, "city": "Zurich"},
    {"id": "f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8z6", "name": "Workshop on Data Mining and Big Data", "edition": 8, "city": "Stockholm"},
    {"id": "g1h2i3j4k5l6m7n8o9p0q1r2s3t4u5v6w7x8a7", "name": "Workshop on Natural Language Processing", "edition": 10, "city": "London"},
    {"id": "h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y9b8", "name": "Workshop on Software Engineering and Testing", "edition": 13, "city": "Amsterdam"},
    {"id": "i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z0c9", "name": "Workshop on Cloud Computing", "edition": 6, "city": "Copenhagen"},
    {"id": "j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z8a0d1", "name": "Workshop on Human-Computer Interaction", "edition": 18, "city": "Paris"},
    {"id": "k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a9b1e2", "name": "Workshop on Distributed Systems", "edition": 7, "city": "Geneva"},
    {"id": "l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c2f3", "name": "Workshop on Cybersecurity", "edition": 15, "city": "Berlin"},
    {"id": "m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b8c9d3g4", "name": "Workshop on Internet of Things", "edition": 11, "city": "London"},
    {"id": "n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c7d0e4h5", "name": "Workshop on Blockchain Technology", "edition": 4, "city": "Barcelona"},
    {"id": "o1p2q3r4s5t6u7v8w9x0y1z2a3b4c6d7e5f6i6", "name": "Workshop on Artificial Intelligence in Healthcare", "edition": 2, "city": "Madrid"},
    {"id": "p1q2r3s4t5u6v7w8x9y0z1a2b3c4d6e8f0g7j7", "name": "Workshop on Robotics and Automation", "edition": 17, "city": "Zurich"},
    {"id": "q1r2s3t4u5v6w7x8y9z0a1b2c3d5e7f1g8h8k8", "name": "Workshop on Computational Social Science", "edition": 20, "city": "Brussels"},
    {"id": "r1s2t3u4v5w6x7y8z9a0b1c2d3e6f7g2h9i9l9", "name": "Workshop on Bioinformatics and Data Science", "edition": 9, "city": "Frankfurt"}
]

paper_reviews = [
    {"score": 9, "main_feedback": "Novel methodology with significant impact to the field", "decision": "accepted"},
    {"score": 6, "main_feedback": "Solid work but needs minor revisions before final acceptance", "decision": "partially accepted"},
    {"score": 10, "main_feedback": "Transformative results with exceptional experimental design", "decision": "accepted"},
    {"score": 7, "main_feedback": "Technically sound but conclusions need slight moderation", "decision": "accepted"},
    {"score": 8, "main_feedback": "Exceptionally well-written with comprehensive analysis", "decision": "accepted"},
    {"score": 6, "main_feedback": "Adequate but requires moderate revisions to methodology", "decision": "partially accepted"},
    {"score": 7, "main_feedback": "Strong theoretical framework with minor implementation issues", "decision": "accepted"},
    {"score": 9, "main_feedback": "Outstanding contribution with immediate field applicability", "decision": "accepted"},
    {"score": 8, "main_feedback": "Well-executed study with clear practical implications", "decision": "accepted"},
    {"score": 7, "main_feedback": "Valuable contribution despite minor literature gaps", "decision": "accepted"},
    {"score": 6, "main_feedback": "Marginally meets publication standards after revisions", "decision": "partially accepted"},
    {"score": 8, "main_feedback": "Innovative approach with thorough validation", "decision": "accepted"},
    {"score": 9, "main_feedback": "Groundbreaking theoretical framework", "decision": "accepted"},
    {"score": 7, "main_feedback": "Competent research with good potential", "decision": "accepted"},
    {"score": 6, "main_feedback": "Requires substantial revisions but shows promise", "decision": "partially accepted"},
    {"score": 8, "main_feedback": "Excellent practical applications", "decision": "accepted"},
    {"score": 9, "main_feedback": "Masterful synthesis of theory and practice", "decision": "accepted"},
    {"score": 7, "main_feedback": "Solid contribution to the field", "decision": "accepted"},
    {"score": 6, "main_feedback": "Needs significant improvements but has merit", "decision": "partially accepted"},
    {"score": 10, "main_feedback": "Flawless execution with paradigm-shifting results", "decision": "accepted"}
]

affiliations = [
    {"type": "University", "name": "University of Oxford"},
    {"type": "University", "name": "ETH Zurich"},
    {"type": "University", "name": "Technical University of Munich"},
    {"type": "University", "name": "Sorbonne University"},
    {"type": "University", "name": "University of Cambridge"},
    {"type": "University", "name": "KU Leuven"},
    {"type": "University", "name": "University of Amsterdam"},
    {"type": "University", "name": "University of Copenhagen"},
    {"type": "University", "name": "Karolinska Institute"},
    {"type": "University", "name": "University of Helsinki"},
    {"type": "Company", "name": "SAP"},
    {"type": "Company", "name": "Spotify"},
    {"type": "Company", "name": "ASML"},
    {"type": "Company", "name": "Siemens"},
    {"type": "Company", "name": "Nokia"},
    {"type": "Company", "name": "Volkswagen Group"},
    {"type": "Company", "name": "Ericsson"},
    {"type": "Company", "name": "Zalando"},
    {"type": "Company", "name": "ARM Holdings"},
    {"type": "Company", "name": "DeepMind"}
]

# Updated reviews data with scores 6-10 and no "denied" decisions
paper_reviews = [
    {"score": 9, "main_feedback": "Novel methodology with significant impact to the field", "decision": "accepted"},
    {"score": 6, "main_feedback": "Solid work but needs minor revisions before final acceptance", "decision": "partially accepted"},
    {"score": 10, "main_feedback": "Transformative results with exceptional experimental design", "decision": "accepted"},
    {"score": 7, "main_feedback": "Technically sound but conclusions need slight moderation", "decision": "accepted"},
    {"score": 8, "main_feedback": "Exceptionally well-written with comprehensive analysis", "decision": "accepted"},
    {"score": 6, "main_feedback": "Adequate but requires moderate revisions to methodology", "decision": "partially accepted"},
    {"score": 7, "main_feedback": "Strong theoretical framework with minor implementation issues", "decision": "accepted"},
    {"score": 9, "main_feedback": "Outstanding contribution with immediate field applicability", "decision": "accepted"},
    {"score": 8, "main_feedback": "Well-executed study with clear practical implications", "decision": "accepted"},
    {"score": 7, "main_feedback": "Valuable contribution despite minor literature gaps", "decision": "accepted"},
    {"score": 6, "main_feedback": "Marginally meets publication standards after revisions", "decision": "partially accepted"},
    {"score": 8, "main_feedback": "Innovative approach with thorough validation", "decision": "accepted"},
    {"score": 9, "main_feedback": "Groundbreaking theoretical framework", "decision": "accepted"},
    {"score": 7, "main_feedback": "Competent research with good potential", "decision": "accepted"},
    {"score": 6, "main_feedback": "Requires substantial revisions but shows promise", "decision": "partially accepted"},
    {"score": 8, "main_feedback": "Excellent practical applications", "decision": "accepted"},
    {"score": 9, "main_feedback": "Masterful synthesis of theory and practice", "decision": "accepted"},
    {"score": 7, "main_feedback": "Solid contribution to the field", "decision": "accepted"},
    {"score": 6, "main_feedback": "Needs significant improvements but has merit", "decision": "partially accepted"},
    {"score": 10, "main_feedback": "Flawless execution with paradigm-shifting results", "decision": "accepted"}
]


# Function to assign event attributes based on paper type
def assign_event_attributes(entry):
    if entry.get("type") == "Conference":
        event = random.choice(conferences)
    elif entry.get("type") == "Workshop":
        event = random.choice(workshops)
    elif entry.get("type") == "Journal":
        event = random.choice(journals)
    else:
        event = random.choice(journals) 
    
    entry["eventid"] = event["id"]
    entry["event_name"] = event["name"]
    entry["edition"] = event["edition"]
    entry["city"] = event["city"]
    return entry

# Function to update the type attribute
def update_type(entry):
    if entry.get("type") == "Journal Articles":
        entry["type"] = "Journal"
    elif entry.get("type") == "Conference and Workshop Papers":
        entry["type"] = "Conference"
    elif entry.get("type") == "Editorship":
        entry["type"] = "Workshop"
    return entry





