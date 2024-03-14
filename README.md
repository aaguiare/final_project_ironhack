<p align="left"><img src="https://cdn-images-1.medium.com/max/184/1*2GDcaeYIx_bQAZLxWM4PsQ@2x.png"></p>

## Ironhack Data PT MAD - Final Project - The Recycling Act

This README file includes the details of the repository elements required for the final project within Data Analytics Bootcamp in Ironhack Madrid.
The project consists of the data exploration, visualization and modellization of the data from recycling bings in the city of Madrid and the list of legal and illegal ladfills in the community of Madrid. 

**Data**

- Bin location and type information of the city of Madrid from the open data website datos.madrid.es/portal/site/egob
- List of illegal and legal landfills of the community of Madrid 
- API connection for GPS routes from openrouteservice.org

**Resources in this repository**

This repository will include the following elements (apart from the ones defined in **Data**): 

- All the modules used to create the streamlit app that will be defined below
- All the essential notebooks for data exploration and data modeling

```

📁 Folder structure
└── project
    ├── README.md
    ├──.gitignore    
    ├── modules_app
        ├──trials
        ├──acquisition.py
        ├──api.py
        ├──app_main.py
    ├── notebooks
        ├──data_exploration_bins.ipynb
        ├──data_preprocessing_landfills.ipynb
        ├──Model preparation_combined dfs.ipynb
    └── data
        ├──Madrid
            ├──200284-0-puntos-limpios-fijos.csv
            ├──Contenedores_varios.csv
            ├──ContenedoresRopa.csv
            ├──Marquesinas_contenedores_pilas_2022.csv
            ├──puntos_negros.csv
            ├──PuntosLimpiosMoviles.csv
            ├──RecogidaContenedoresAceiteUsado.csv
            ├──residuos_gestores.csv
            ├──vertederos_clean.csv


```

💥**Technology stack**

Python, SkLearn, Pandas, Pydeck, Streamlit

👀**Context**

❗*Note that all Streamlit content is set in spanish as it's oriented to spanish market*❗

This repository is the final project for the Part Time Data Analytics Bootcamp in March 2024, which had the following goals:

- Create a streamlit app to visualize all the recycling bins in madrid by type, as well as sharing the most optimal route from the start point of the user to the combinations of bins that are being targeted by residue type. Defined in modules_app py files (app_main) and displayed in local.
- Create a modelization to extrapolate the number of illegal landfills that could be found in the community of Madrid by the features of the ones already found in the territory. Process can be found in the Jupyter notebooks (data_preprocessing_landfills, Model preparation_combined dfs) and the results are included visually in Streamlit app as a map.

💣 **Reporting Architecture**


*Goal 1: Streamlit App for Visualizing Recycling Bins in Madrid*

1. Data Collection and Preparation:

Gather data on recycling bin locations and types in Madrid.
Clean and preprocess the data to ensure it includes coordinates (latitude and longitude), bin types, and any other relevant information.

2. Development Environment Setup:

Install necessary Python libraries, including Streamlit, pandas, numpy, geopy and requests.

3. App Design and Development:

Create the Streamlit app structure, defining user input areas (for starting point and targeted residue types) and output display areas (for maps and routes).
Integrate mapping functionality using Pydeck to visualize bin locations on a map.

4. Route Optimization:

Implement route optimization logic to calculate the most optimal route from the user's start point to the targeted bins. The API used for routing is Open Route Service.

5. Testing and Refinement:

Test the app with various scenarios to ensure accurate visualization and routing.
Refine the user interface based on feedback to improve usability.


*Goal 2: Modelization to Extrapolate Illegal Landfills in Madrid*

1. Data Collection and Exploration:

Collect data on known illegal and legal landfill sites, including their features like location, special features, and types of waste found.
Explore the dataset to understand the distribution of features and identify any patterns.

2. Data Cleaning and Preprocessing:

Clean the data by handling missing values and outliers.
Preprocess the data by encoding categorical variables and normalizing numerical features.

3. Feature Engineering:

Derive new features that may be indicative of illegal landfill occurrences, such as proximity to nature areas or rivers.
Select relevant features for the model based on correlation analysis or domain knowledge.

4. Model Selection and Training:

Split the data into training and testing sets and train the model on the training set.
Test classification models for predictive modeling, such as XGBoost or Logistic Regression.

5. Model Evaluation and Tuning:

Evaluate the model's performance using appropriate metrics, such as accuracy.

6. Extrapolation visualizationand Analysis:

Use the trained model to predict potential illegal landfill sites across the community of Madrid.
Analyze the predictions to identify patterns or hotspots for illegal landfills, while visualizing the first results in map on Stremlit app.

💩 **ToDo**

As next steps and continuous improvements: 

- Expand the streamlit application and modellization to the rest of territories of Spain (there are already data to be used in data folder)


💌 **Contact info**

Hi! I am Ana! 🎟
Feel free to contact me at teamurjc@gmail.com. Happy to chat!