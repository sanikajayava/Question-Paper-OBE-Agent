import json

db_path = "data/real_question_bank.json"

with open(db_path, "r", encoding="utf-8") as f:
    data = json.load(f)

def inject_questions(subject, exam_type, batch, texts):
    for i, text in enumerate(texts):
        q_id = f"Q_{subject[:3].upper()}_{exam_type}_{i+1}"
        if not any(q["id"] == q_id for q in data):
            data.append({
                "id": q_id,
                "subject": subject,
                "exam_type": exam_type,
                "year": "2026",
                "batch": batch,
                "question_text": text
            })

# 1. Cloud Computing ESA 2026
inject_questions("Cloud Computing", "ESA", "Oct 2025 - Feb 2026", [
    "Explain the architecture of the Leaf-Spine network topology and how it solves congestion issues. (10 Marks)",
    "Design a multi-cloud strategy for an e-commerce company to avoid vendor lock-in. (15 Marks)",
    "Discuss the role of Docker containers in modern software deployment. (10 Marks)",
    "Analyze how Kubernetes manages container orchestration at scale. (15 Marks)",
    "What are the different cloud service models (IaaS, PaaS, SaaS)? (10 Marks)",
    "Explain the concept of serverless computing with real-world examples. (10 Marks)",
    "How does virtualization differ from containerization? (10 Marks)",
    "Describe the working of Ansible for Configuration Management. (10 Marks)",
    "Write a detailed note on Infrastructure as Code (IaC). (10 Marks)",
    "Explain the security challenges in Cloud Computing. (10 Marks)"
])

# 2. Deep Learning ESA 2026
inject_questions("Deep Learning", "ESA", "Oct 2025 - Feb 2026", [
    "Explain the architecture of Convolutional Neural Networks (CNN). (10 Marks)",
    "Compare and contrast RNN and LSTM networks. (10 Marks)",
    "Design a neural network for image classification using transfer learning. (15 Marks)",
    "What are the activation functions? Compare ReLU and Sigmoid. (10 Marks)",
    "Explain the concept of Dropout in preventing overfitting. (10 Marks)",
    "Describe the working of YOLO for real-time object detection. (15 Marks)",
    "Explain how GANs (Generative Adversarial Networks) work. (10 Marks)",
    "Discuss the challenges in training deep neural networks. (10 Marks)",
    "Write a note on the UNet architecture for image segmentation. (10 Marks)",
    "Explain the concept of Attention Mechanisms in Deep Learning. (10 Marks)"
])

# 3. Cyber Security ESA 2025
inject_questions("Cyber Security", "ESA", "Oct 2024 - Feb 2025", [
    "Explain the CIA triad and its importance in cyber security. (10 Marks)",
    "Discuss the types of cybercrimes with real-world examples. (10 Marks)",
    "Analyze the Indian IT Act 2000 and its amendments. (15 Marks)",
    "Explain how social engineering attacks are planned and executed. (10 Marks)",
    "Describe the role of Security Operations Centers (SOC). (10 Marks)",
    "What is SIEM? How does it help in incident response? (10 Marks)",
    "Explain the working of firewalls and Intrusion Detection Systems (IDS). (15 Marks)",
    "Design a recovery plan for a ransomware attack. (10 Marks)",
    "Discuss the concept of Zero Trust Architecture. (10 Marks)",
    "Explain the different types of cyber forensics tools. (10 Marks)"
])

# 4. Gen AI ESA 2026
inject_questions("Gen AI", "ESA", "Oct 2025 - Feb 2026", [
    "Explain the architecture of the Transformer model. (15 Marks)",
    "What is self-attention and multi-head attention? (10 Marks)",
    "Discuss the working of Word2Vec (CBOW and Skip-Gram). (10 Marks)",
    "Explain the architecture of StyleGAN for image generation. (15 Marks)",
    "Compare Zero-Shot, Few-Shot, and Chain-of-Thought prompting. (10 Marks)",
    "Describe the working of Diffusion Models (like Stable Diffusion). (15 Marks)",
    "Explain how Large Language Models (LLMs) like GPT work. (10 Marks)",
    "What are Denoising Autoencoders? How are they used? (10 Marks)",
    "Explain the concept of CLIP for aligning text and images. (10 Marks)",
    "Describe the pipeline of DALL-E 2 for image generation. (10 Marks)"
])

with open(db_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("✅ Database expanded with 40 high-quality questions!")