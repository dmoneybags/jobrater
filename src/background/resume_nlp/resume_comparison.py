import re
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util

# Download NLTK stop words list if not already downloaded
class ResumeComparison:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    stop_words = set(stopwords.words('english'))

    def preprocess(text):
        # Lowercase the text
        text = text.lower()
        
        # Remove special characters except for sentence boundary punctuation
        #text = re.sub(r'[^a-zA-Z0-9\s\.\!\?]', '', text)
        text = ' '.join([word for word in text.split() if word not in ResumeComparison.stop_words])
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    # Split text into sentences
    def split_into_sentences(text):
        #sentences 
        sentences_pre_newline_split = sent_tokenize(text)
        #final copy to return
        sentences = sentences_pre_newline_split
        i = 0
        for sentence in sentences_pre_newline_split:
            if "\n" in sentence or "?" in sentence or "!" in sentence or "." in sentence:
                #split it into the actual sentences 
  
                split_newline_sentences = re.split(r'[?.!\n]+', sentence)
                split_newline_sentences = [re.sub(r'[^a-zA-Z0-9\s]', '', text) for text in split_newline_sentences]
                sentences[i] = split_newline_sentences.pop(0)
                split_newline_sentences.reverse()
                for new_sentence in split_newline_sentences:
                    sentences.insert(i + 1, new_sentence)
                i += 1
        return sentences

    def get_embeddings(text):
        preprocessed_text = ResumeComparison.preprocess(text)
        sentences = ResumeComparison.split_into_sentences(preprocessed_text)
        return ResumeComparison.model.encode(sentences)
    def get_similarity_matrix(job_description_text, resume_text):
        job_embeddings = ResumeComparison.get_embeddings(job_description_text)
        resume_embeddings = ResumeComparison.get_embeddings(resume_text)
        return util.pytorch_cos_sim(job_embeddings, resume_embeddings).cpu().numpy()
    def compare_embeddings(similarity_matrix):
        # Flatten the matrix and get indices sorted by values
        sorted_indices = np.argsort(similarity_matrix.flatten())[::-1]

        # Convert flattened index to 2D index
        sorted_indices_2d = np.unravel_index(sorted_indices, similarity_matrix.shape)

        # Zip row and column indices together
        sorted_index_list = list(zip(sorted_indices_2d[0], sorted_indices_2d[1]))

        return sorted_index_list
    def serialize_similarity_matrix(similarity_matrix):
        simalarity_matrix_numpy = similarity_matrix.numpy()
        similarity_matrix_str = np.array2string(simalarity_matrix_numpy)
        return similarity_matrix_str
    def serialize_sorted_index_list(sorted_index_list):
        sorted_index_list = [list(a) for a in sorted_index_list]
        sorted_index_numpy = np.array(sorted_index_numpy)
        return np.array2string(sorted_index_numpy)
    def print_comparisons(job_description, resume):
        job_sentences = ResumeComparison.split_into_sentences(job_description)
        resume_sentences = ResumeComparison.split_into_sentences(resume)
        similarity_matrix = ResumeComparison.get_similarity_matrix(job_description, resume)
        sorted_index_list = ResumeComparison.compare_embeddings(similarity_matrix)
        i=0
        for (job_description_sentence_index, resume_sentence_index) in sorted_index_list:
            print(f"================= NUMBER {i} ================")
            print("SENTENCES:")
            print(f"JOB DESCRIPTION SENTENCE: {job_sentences[job_description_sentence_index]}")
            print(f"RESUME DESCRIPTION SENTENCE: {resume_sentences[resume_sentence_index]}")
            print(f"VALUE: {similarity_matrix[job_description_sentence_index][resume_sentence_index]}")
            i += 1

job_description = '''
About the job
About Us

Day to day life has room for improvement.
 
That was our basic thinking when we founded simplehuman in 2000. Our mission is to bring high-performance and sustainable innovation to basic but essential tasks in our daily routine at home. Through new technologies, meticulous engineering and an obsession for improvement, we find new and better ways to achieve basic but important daily tasks. 

About the role

simplehuman is seeking an experienced Firmware/Embedded Software Engineer to join our group of close-knit engineers in our Product team. Job scope includes firmware development, modification, testing, and troubleshooting for all stages of the product life cycle. This position directly impacts the simplehuman product line and brand. As we continue to expand into more technology-enabled products, our Firmware team is becoming an increasingly important part of our greater Product team – responsible for our award-winning consumer products that make life more efficient at home! This is a full-time role in our Torrance, CA office, with some opportunity for hybrid working. This is NOT a remote position. 

Responsibilities include:
· Develop, design and review firmware for new products and prototypes
· Modify firmware for improved product performance and the addition of new features
· Troubleshoot firmware/hardware related issues/improvements that arise during production
· Work with Mechanical and QC engineers to investigate, test, and make improvements
· Evaluate new technology platforms for new product feasibility/validation
· Communicate with technical vendors during product development
 
About You

· BS in Computer Science, Computer/Electrical Engineering or equivalent degree. MS preferred
· 2+ years’ experience as a firmware or embedded software engineer in the consumer electronics industry
· Experience developing firmware for micro-controllers inclu. PIC, ARM-Cortex Core STM32 (MUST-HAVE) 
· Fluency in C/C++ (MUST HAVE)
· Familiarity with RTOS based software architecture
· Experience with peripheral communication protocols (I2C, SPI, UART, PWM)
· Experience with wireless connectivity such as Wi-Fi, Bluetooth
· Experience with acoustics microphone/speaker integrations
· Experience with touch screens display integrations
· Experience with Linux/Android based processor software development
· Ability to understand hardware schematics
· Ability to work on multiple projects
· Ability to work independently
· Ability to work with internal and external partners to solve problems creatively
· A hands-on approach to quickly evaluate and test out prototypes and solutions
· Excellent verbal and written communications

Culture
 
We have the stability of an established company, but the soul of a start-up. We value ingenuity, precise communications, fast iteration and scrappiness. Our teams are tight-knit with a work hard, play hard tradition – we take pride in individual and team success and push boundaries to make the best products. And we only build products we love to use ourselves. 
 
· Cool office with full-court gym + fitness activities/classes (basketball, yoga, volleyball, badminton, krav maga, more) + weight room 
· Free weekly breakfasts + birthday celebrations + holiday parties/trips + juice club
· Great benefits + Competitive compensation
· Generous simplehuman product discounts
'''
resume = '''
Jake Johnson
Swift Programmer

Contact Information:

Phone: (555) 123-4567
Email: jake.johnson@example.com
LinkedIn: linkedin.com/in/jakejohnson
GitHub: github.com/jakejohnson
Summary:

Experienced Swift programmer with a strong background in Objective-C, having developed apps since 2013. Demonstrates a comprehensive understanding of mobile application development, user interface design, and performance optimization. Proven ability to deliver high-quality applications in fast-paced environments.

Education:

Sonoma State University
Bachelor of Science in Computer Science
Graduation Date: May 2013

Professional Experience:

Snapchat, Inc.
Senior iOS Developer
June 2016 – June 2018

Developed and maintained core features of the Snapchat app using Swift and Objective-C.
Collaborated with cross-functional teams to design, develop, and release new features.
Optimized app performance, reducing load times by 30%.
Implemented A/B testing to enhance user experience and engagement.
Conducted code reviews and mentored junior developers.
XYZ Web Design Company
Junior Mobile Developer
December 2014 – May 2016

Designed and developed custom iOS applications for clients.
Migrated legacy Objective-C code to Swift, improving maintainability and performance.
Worked closely with designers and clients to translate requirements into functional apps.
Implemented RESTful APIs and integrated third-party services.
Skills:

Programming Languages: Swift, Objective-C, JavaScript, HTML/CSS
Mobile Development: iOS, UIKit, CoreData, CoreAnimation
Tools & Technologies: Xcode, Git, JIRA, RESTful APIs, Firebase
Other Skills: Agile Methodologies, Code Reviews, Unit Testing, Mentorship
Projects:

Project Name: Social Connect App

A social networking app designed to connect people with similar interests.
Implemented user authentication, profile management, and real-time messaging features.
Technologies used: Swift, Firebase, UIKit.
Project Name: Health Tracker App

An app to help users track their health metrics and achieve their fitness goals.
Integrated with HealthKit to retrieve and display user health data.
Technologies used: Swift, HealthKit, CoreData.
Certifications:

Apple Certified iOS Developer
Scrum Master Certified (SMC)
'''
if __name__ == "__main__":
    ResumeComparison.print_comparisons(job_description, resume)