## Lose It! Forum Analysis: Yo-Yo Dieting

### Business Understanding
With over 24 million subscribers, Lose It! is a leading app facilitating weight management through calorie counting and diet/exercise logging. The app offers an array of data science tools and dashboards to inform and motivate users. However, the current feature set offers little to directly illuminate user adherence to the very practice of adhering to the app itself--that is, to prevent “yo-yo dieting,” or going on and dropping off the app. The Lose It! Forum Analysis will mine user insights to understand the most common causes cited for “falling off the wagon” as well as strategies to stick with the program. If the data allows, this project may also characterize forum participants by participation, sentiment and “communities” defined by shared forum threads.

### Data Understanding
Lose It! hosts an online forum consisting of tens of thousands of threads (“topics”) containing hundreds of thousands of individual messages in html text. Forum thread and responses contain a vast textual database of ideas, while the subject lines, posting dates, threads and user profiles offer data that could help track the evolution of conversations and ad-hoc communities addressing the problem of yo-yo dieting. The company that created and hosts the app has been unresponsive to my requests for data or an API, so the forum data will need to be web-scraped. 

### Data Preparation
After web-scraping, the major tasks will be the tokenizatition and vectorization of message threads along with the extraction and storage of user-participation data in a database. The project will drive toward a database organized into a schema such as below:

```
TOPIC TABLE:
TOPIC | TOPIC ID* | LIBRARY | #MESSAGES | AUTHOR | #VIEWS | BEGIN DATE | LAST MESSAGE AUTHOR | LAST MSG DATE

     * Encoded by Lose It! in URLs

MESSAGE TABLE:
USER | #MSGS POSTED | TOPIC | TOPIC ID | DATE OF POST | TEXT

USER TABLE:
USER | JOINED | CITY | STATE | MEMBER SINCE | BIO | INTERESTS | (others)?
```

### Modeling
NLP to identify keywords and to cluster ideas (causes and remedies). Random Forest for classification of users or threads (as defined by the features of their message contents) and graphing to identify influential/central users. 

### Evaluation
TBD

### Deployment
Minimum viable product: A webpage where users struggling with motivation can select from among a limited number of the most commonly cited reasons for “backsliding.” The webpage will return a selection of the most relevant posts, highlighting the most common strategies to address the problem selected by the user.
