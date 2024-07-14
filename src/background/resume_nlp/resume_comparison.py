import re
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util

# Download NLTK stop words list if not already downloaded
class Resume_Comparison:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    nltk.download('stopwords')
    nltk.download('punkt')
    stop_words = set(stopwords.words('english'))

    def preprocess(text):
        # Lowercase the text
        text = text.lower()
        
        # Remove special characters except for sentence boundary punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.\!\?]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    # Split text into sentences
    def split_into_sentences(text):
        return sent_tokenize(text)
    def get_similarity_matrix(resume_text, job_description_text):
        preprocessed_job_description = Resume_Comparison.preprocess(job_description_text)
        preprocessed_resume = Resume_Comparison.preprocess(resume_text)

        print("TEXTS AFTER PREPROCESSING")
        print(preprocessed_job_description)
        print(preprocessed_resume)

        job_sentences = Resume_Comparison.split_into_sentences(preprocessed_job_description)
        resume_sentences = Resume_Comparison.split_into_sentences(preprocessed_resume)

        print("TEXTS SPLITTING SENTENCES")
        print(job_sentences)
        print(resume_sentences)

        # Encode each sentence
        job_embeddings = Resume_Comparison.model.encode(job_sentences, convert_to_tensor=True)
        resume_embeddings = Resume_Comparison.model.encode(resume_sentences, convert_to_tensor=True)

        print("EMBEDDINGS")
        print(job_embeddings)
        print(resume_sentences)
        # Compute similarities
        similarity_matrix = util.pytorch_cos_sim(job_embeddings, resume_embeddings).cpu().numpy()

        print(similarity_matrix)

        # Flatten the matrix and get indices sorted by values
        sorted_indices = np.argsort(similarity_matrix.flatten())[::-1]

        # Convert flattened index to 2D index
        sorted_indices_2d = np.unravel_index(sorted_indices, similarity_matrix.shape)

        # Zip row and column indices together
        sorted_index_list = list(zip(sorted_indices_2d[0], sorted_indices_2d[1]))

        print("Sorted indices by largest value:")
        i = 0
        for (job_description_sentence_index, resume_sentence_index) in sorted_index_list:
            print(f"================= NUMBER {i} ================")
            print("SENTENCES:")
            print(f"JOB DESCRIPTION SENTENCE: {job_sentences[job_description_sentence_index]}")
            print(f"RESUME DESCRIPTION SENTENCE: {resume_sentences[resume_sentence_index]}")
            print(f"VALUE: {similarity_matrix[job_description_sentence_index][resume_sentence_index]}")
            i += 1


job_description = '''
About the job
ADP is hiring a Sales Representative, Human Resources Outsourcing (HRO).

Are you ready for your next best job where you can elevate your financial future?
Are you looking to grow your career with a formal career path at an established, respected, global leader?
Do you want to join a fast-paced, inclusive environment with a culture of collaboration and belonging?

If so, this may be the opportunity you've been searching for. Read on and decide for yourself.

In this role, you will close sales and win new business within a defined territory. You'll attend our award-winning training program and join a sales team that works with both new and existing clients to sell human resources solutions, making employees' lives better with high-quality benefits offerings across the hire-to-retire spectrum. Daily, you will cultivate relationships with Human Resources and executive decision-makers, set appointments, gather leads from established internal partners, and assess buyer needs to present the best ADP solutions.

You will use your ability to manage multiple sales processes at the same time through various stages in the sales process, as well as document them, sticking with the process through implementation until your new business is up and running on the solutions you sell. As you see more and more deals cross the finish line, you'll reap the rewards with industry-leading compensation, benefits, luxurious incentive trips, and awards. As you strive to grow your career, leaders will back your desire to pursue advancement and provide continual sales training.

A little about ADP: We are a global leader in human resources technology, offering the latest AI and machine learning-enhanced payroll, tax, human resources, benefits, and much more. We believe our people make all the difference in cultivating an inclusive, down-to-earth culture that welcomes ideas, encourages innovation, and values belonging. We've received recognition as a global Best Places to Work and a recipient of many prestigious awards for diversity, equity, and inclusion, including a DiversityInc® Top 50 Company, Best CEO and company for women, LGBTQ+, multicultural talent, and more. As part of our deep DEI commitment, our CEO has joined the OneTen coalition to create one million jobs for Black Americans over the next ten years. Learn more about DEI at ADP on our YouTube channel: http://adp.careers/DEI_Videos.

Ready to #MakeYourMark? Apply now!

To learn more about Sales at ADP, watch here: http://adp.careers/Sales_Videos

WHAT YOU'LL DO: Responsibilities

Grow Our Business While Growing Yours: You will work within a defined, protected territory to close sales, win business, and reach sales goals by implementing a top-down sales strategy. 
Turn Prospects into Loyal and Referring Clients: You will close sales by recommending the right solutions to help our clients understand and solve their real business needs. Plus, you'll earn referral business by networking with existing and soon-to-be clients and forging partnerships in-person and over the phone with decision-makers.
Deepen Relationships Across the ADP Family: In addition to cloud-based human resources solutions, you will strategically cross-sell with other ADP associates to cultivate additional business within existing accounts; you will make life-long friendships here.
Collaborate Daily. You will serve as a trusted advisor, partner, and ADP ambassador to your clients, internal partners, and overall network while demonstrating grace under pressure and the highest ethical standards.

TO SUCCEED IN THIS ROLE: Required Qualifications

Positive Self-Starter. You have an upbeat, persistent style and the ability to cold call without fear of rejection. You can manage your time well, prioritize deliverables, and multi-task with the best of them. In addition, you can present your ideas in a clear, professional manner on paper, in-person, and over the phone. 
Strategic Closer. You have an established network and experience carrying a quota in outside business-to-business sales. You have an impressive track record of closing sales, winning clients, and managing a territory and relationships. 
Proven Winner. You have an ambitious spirit and thrive under pressure, motivating you to not only hit sales quotas but exceed them.

Required

A college degree is great but not required. What's more important is having the skills to do the job. If you don't have a college degree, other acceptable experience could include:

Three years of business-to-business sales experience (preferably field sales) within a results-driven environment.
Military experience -- skills including teamwork, resilience, negotiation, trust-building, and a "never lose" mentality will help you build team and client relationships, identify solutions, and achieve success.

Bonus points for these: Preferred Qualifications

Ability to successfully build a network and effectively use social media for sales

You'll Love Working Here Because You Can

Be yourself in a culture that values equity, inclusion, and belonging and creates a safe space for diverse perspectives and insights.
Belong by joining one of nine Business Resource Groups where you can connect globally with networks and allies who share common interests and experiences.
Grow your career in an agile, fast-paced environment with plenty of opportunities to progress.
Continuously learn. Ongoing training, development, and mentorship opportunities for even the most insatiable learner.
Be your healthiest. Best-in-class benefits start on Day 1 because healthy associates are happy ones.
Balance work and life. Resources and flexibility to more easily integrate your work and your life.
Focus on your mental health and well-being. We're here to provide exceptional service to our clients, and none of that happens without each of us taking care of ourselves and being there for one another.
Join a company committed to giving back and generating a lasting, positive impactupon the communities in which we work and live. 
Get paid to pay it forward. Company-paid time off for volunteering for causes you care about.

Base salary offers for this position may vary based on factors such as location, skills, and relevant experience.

Some positions may include additional compensation in the form of bonus, equity or commissions.

We offer the following benefits: Medical, Dental, Vision, Life Insurance, Matched Retirement Savings, Wellness

Program, Short-and Long-Term Disability, Charitable Contribution Match, Holidays, Personal Days & Vacation,

Paid Volunteer Time Off, and more.

Compensation Range for this role is $42,400 - $92,000/ year

What are you waiting for? Apply now!

Base salary offers for this position may vary based on factors such as location, skills, and relevant experience. Some positions may include additional compensation in the form of bonus, equity or commissions. We offer the following benefits: Medical, Dental, Vision, Life Insurance, Matched Retirement Savings, Wellness Program, Short-and Long-Term Disability, Charitable Contribution Match, Holidays, Personal Days & Vacation, Paid Volunteer Time Off, and more. The compensation for this role is $42,400.00 - $92,000.00 / Year

Diversity, Equity, Inclusion & Equal Employment Opportunity at ADP: ADP is committed to an inclusive, diverse and equitable workplace, and is further committed to providing equal employment opportunities regardless of any protected characteristic including: race, color, genetic information, creed, national origin, religion, sex, affectional or sexual orientation, gender identity or expression, lawful alien status, ancestry, age, marital status, protected veteran status or disability. Hiring decisions are based upon ADP’s operating needs, and applicant merit including, but not limited to, qualifications, experience, ability, availability, cooperation, and job performance.

Ethics at ADP: ADP has a long, proud history of conducting business with the highest ethical standards and full compliance with all applicable laws. We also expect our people to uphold our values with the highest level of integrity and behave in a manner that fosters an honest and respectful workplace. Click https://jobs.adp.com/life-at-adp/ to learn more about ADP’s culture and our full set of values.
'''
resume = '''
Daniel DeMoney
(408) 444-3650 • dandemoney@gmail.com •  Pomona, California 91768

EXPERIENCE
California Polytechnic Pomona, Consumer Insights Consultancy	Pomona, CA
Consultant	Aug 2022 – May 2023
	•	Collaborating with a small group of motivated students and faculty to create and execute a marketing research initiative to help a multi-million-dollar client increase profits.
	•	Successfully prepared a research design to conduct market research on the client’s market.
	•	Using machine learning techniques with R to gain insight from over a decade of transaction data.
Coherent (formerly Finisar/II-VI)	San Jose, CA
Sales Intern	May 2022 – Aug 2022
	•	Worked closely with Sales Managers, Product Line Managers, and Senior VPs to execute deliverables on deals worth upwards of $10 million.
	•	Helped lead an initiative to tabulate excess inventory into a database and sell pieces to brokers, netting over $1 million in revenue.
	•	Created monthly forecasts using Demantra.
	•	Conducted daily cold calls to prospect new clients.
	•	Organized sales cycle data within Salesforce.
California Polytechnic Pomona, Project Hatchery, Team Apollo	Pomona, CA
Sales Lead	Aug 2021 – May 2022
	•	Cofounded a team to develop and market a wearable blood pressure measurement device.
	•	Helped allocate a $4,000 budget, develop project timelines, and program Bluetooth software for the prototype.
Office Depot	Los Gatos, CA
Sales Specialist	Aug 2020 – May 2021
	•	Promoted to Sales Specialist from Sales Advisor within 2 months as a result of exceeding my quotas.
	•	Gained experience selling and knowledge of Epson, Hp, Dell, and Microsoft products.
	•	Oversaw the sales of laptops and desktop computers and increased tech bundle sales by 30%.
	•	Lead the store in loyalty account signups for 6 months straight.

EDUCATION
California Polytechnic Pomona	Pomona, CA
B.S. Business Marketing	May 2023

REFERENCES
Andres Gomez
	•	Coherent, Former Account Manager 
	•	(919) 943-8223, andres1.gomez@intel.com

Stephen Cash
	•	Coherent, Former Account Manager
	•	(408) 813-8629, stephen.cash@gmail.com
'''
Resume_Comparison.get_similarity_matrix(resume, job_description)