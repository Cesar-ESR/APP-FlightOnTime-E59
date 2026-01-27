'use client';

import { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { ChevronDown } from 'lucide-react';
import TitlePage from '../components/TitlePage';

const chapters = [
  {
    id: 1,
    title: 'Chapter 1. Introduction and Project Purpose',
    content: [
      `FlightOnTime is a flight delay prediction system designed to anticipate, based on historical data and Machine Learning techniques, whether a flight will depart on time or with a significant delay. The project stems from a specific need in the aviation industry: delays not only affect the passenger experience but also generate operational inefficiencies, extra costs, and planning issues that could be mitigated if the risk is known in advance.`,
      `The main objective of the system is not to retrospectively explain why a delay occurred, but to <strong>estimate the risk of it occurring before takeoff</strong>, when preventive decisions can still be made. To achieve this, FlightOnTime combines a robust Data Science model with an architecture designed for real production use, exposing predictions through a REST API.`,
      `This approach turns the project into a complete solution that goes beyond exploratory analysis or experimental modeling, positioning itself as a practical tool to support decision-making.`
    ]
  },
  {
    id: 2,
    title: 'Chapter 2. Data Science Approach and Problem Definition',
    content: [
      'From a Data Science perspective, the problem was formulated as a <strong>binary classification problem</strong>, where the model must predict whether a flight will belong to one of the following classes:',
      `<ul>
        <li>• On-time flight</li>
        <li>• Flight with a delay equal to or greater than 15 minutes</li>
      </ul>`,
      `The target variable used is DEP_DEL15, widely used in aeronautical datasets, which ensures consistency with real industry standards. This definition allows the prediction to have a clear operational meaning that is directly interpretable by both technical and non-technical users.`,
      `The main challenge lies in the high variability of the air system: multiple factors interact simultaneously, from weather conditions to specific operational patterns of airlines, airports, and time slots. Therefore, the project's approach prioritizes models capable of capturing complex relationships without sacrificing robustness.`
    ]
  },
  {
    id: 3,
    title: 'Chapter 3. Data Used and Dataset Enrichment',
    content: [
      'The model was trained using a large-scale dataset composed of approximately <strong>35.7 million US domestic flights</strong>. This volume of data allows for the capture of structural patterns in the aviation system that would not be visible in small or limited datasets.',
      'In addition to basic flight information, the project incorporates a <strong>data enrichment</strong> process, integrating external variables relevant to delay prediction. Specifically, historical weather information and geolocation data obtained through specialized APIs and sources evaluated for their reliability were added.',
      `This enrichment is one of the project's main strengths, as it introduces factors that directly influence flight punctuality and are often omitted in simplified approaches.`
    ]
  },
  {
    id: 4,
    title: 'Chapter 4. Variables and Features Considered by the Model',
    content: [
      'The final set of features used by the model was carefully selected to meet two fundamental criteria: predictive relevance and pre-flight availability.',
      `<p><strong>Temporal Variables</strong></p>
      <p>These variables allow for capturing seasonality and hourly patterns:</p>
      <ul>
        <li>• Year (YEAR)</li>
        <li>• Month (MONTH)</li>
        <li>• Day of the week (DAY_OF_WEEK)</li>
        <li>• Scheduled minute of the day (sched_minute_of_day)</li>
      </ul>`,

      `<p><strong>Operational Variables</strong></p>
      <p>Represent characteristics specific to the flight:</p>
      <ul>
        <li>• Airline (OP_UNIQUE_CARRIER)</li>
        <li>• Origin airport (ORIGIN)</li>
        <li>• Destination airport (DEST)</li>
        <li>• Flight distance (DISTANCE, DIST_MET_KM)</li>
      </ul>`,

      `<p><strong>Weather Variables</strong></p>
      <p>Introduce the impact of the meteorological environment:</p>
      <ul>
        <li>• Temperature (TEMP)</li>
        <li>• Wind speed (WIND_SPD)</li>
        <li>• Hourly precipitation (PRECIP_1H)</li>
        <li>• Climate severity index (CLIMATE_SEVERITY_IDX)</li>
      </ul>`,

      `<p><strong>Discarded Variables</strong></p>
      <p>Variables that could generate data leakage, were not available in real-time, or did not provide clear predictive value were removed, such as:</p>
      <ul>
        <li>• DEP_DELAY</li>
        <li>• FL_DATE</li>
        <li>• CRS_DEP_TIME</li>
        <li>• City names instead of standardized codes</li>
      </ul>`,

      `<p>This refinement reinforces the realistic and productive nature of the model.</p>`
    ]
  },
  {
    id: 5,
    title: 'Chapter 5. Machine Learning Model',
    content: [
      `<p>After evaluating different approaches, the final model selected was <strong>XGBoost</strong>, a gradient boosting algorithm widely used in classification problems with tabular data.</p>`,
      `The choice of XGBoost is based on its ability to:`,
      `<ul>
        <li>• Capture complex non-linear relationships</li>
        <li>• Handle interactions between multiple variables</li>
        <li>• Scale efficiently with large volumes of data</li>
        <li>• Maintain excellent predictive performance</li>
      </ul>`,
      `The model was trained, evaluated, and optimized, reaching the following metrics:`,
      `<ul>
        <li>• Accuracy: 72.32%</li>
        <li>• Recall: 54.30%</li>
        <li>• ROC-AUC: 0.7194</li>
        <li>• Optimized Threshold: 0.5591</li>
      </ul>`,
      `These metrics reflect an appropriate balance between overall accuracy and the ability to identify flights with real risk of delay, prioritizing early detection of the most critical cases.`
    ]
  },
  {
    id: 6,
    title: 'Chapter 6. System Architecture and Production Integration',
    content: [
      'FlightOnTime was designed with a modular and decoupled architecture, clearly separating the responsibilities of each component:',
      `<ul>
        <li>• Data Science Layer: model training, evaluation, and serialization</li>
        <li>• Back-End Layer: model exposure via a REST API</li>
        <li>• Front-End Layer: API consumption by end users</li>
      </ul>`,
      `<p>The model was serialized using <strong>Joblib</strong> and dynamically loaded by the 
    API developed with <strong>FastAPI</strong>. Communication between the Back-End and the model is based on a 
    <strong>previously defined feature contract</strong>, which ensures 
    consistency between training and prediction in production.</p>`
    ]
  },
  {
    id: 7,
    title: 'Chapter 7. System Operation and Input Data',
    content: [
      'From the user or client system perspective, the project operation is simple and transparent.',
      'To request a prediction, basic flight data must be provided to the API, including:',
      `<ul>
        <li>• Airline</li>
        <li>• Origin and destination airport</li>
        <li>• Scheduled departure date and time</li>
        <li>• Necessary information to reconstruct temporal and spatial variables</li>
      </ul>`,
      `The API validates the information, applies the necessary transformations, and executes the predictive model.`
    ]
  },
  {
    id: 8,
    title: 'Chapter 8. Delivered Results and Interpretation',
    content: [
      'As a result, the system returns:',
      'To request a prediction, basic flight data must be provided to the API, including:',
      `<ul>
        <li>• A classification: on-time flight or delayed flight</li>
        <li>• A probability associated with the delay</li>
      </ul>`,
      `This probability should not be interpreted as an absolute certainty, but rather as a risk 
indicator. High values indicate that, given similar historical conditions, there is a high 
probability of delay. This allows for informed decision-making, such as reinforcing operational 
planning, anticipating communications, or prioritizing the monitoring of certain flights.`
    ]
  },
  {
    id: 9,
    title: 'Chapter 9. Project Value and Relevance',
    content: [
      'FlightOnTime demonstrates how Data Science generates real impact when integrated into usable systems. The project combines technical rigor, use of real data, robust modeling, and an architecture designed for production.',
      'It does not promise to eliminate delays, but it does reduce uncertainty, which is one of the major operational problems in the aviation industry. In this sense, the project positions itself as a necessary, scalable solution aligned with real professional practices.',
    ]
  },
];

export default function AboutPage() {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <DashboardLayout>
      <div className="w-full">
        <div className="mb-10">
          <TitlePage title="Technical Manual and Project Reference Document" />
        </div>

        {/* Expandable Cards Section */}
        <div>
          <div className="space-y-4">
            {chapters.map((chapter) => (
              <div
                key={chapter.id}
                className="group"
              >
                <button
                  onClick={() => toggleExpand(chapter.id)}
                  className={`w-full transition-all duration-300 ${
                    expandedId === chapter.id
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-lg'
                      : 'bg-white text-gray-900 rounded-lg hover:shadow-md'
                  } shadow-md hover:shadow-lg p-6 flex items-center justify-between text-left`}
                >
                  <span className="text-lg font-semibold">{chapter.title}</span>
                  <ChevronDown
                    className={`w-6 h-6 transition-transform duration-300 ${
                      expandedId === chapter.id ? 'rotate-180' : ''
                    }`}
                  />
                </button>

                {/* Contenido expandible */}
                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    expandedId === chapter.id ? 'max-h-screen' : 'max-h-0'
                  }`}
                >
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-b-lg shadow-md border-t-2 border-blue-300">
                    <div className="space-y-4 text-gray-800">
                      {Array.isArray(chapter.content) ? (
                        chapter.content.map((item, index) => {
                          // Detectar si el contenido es HTML
                          const isHtml = typeof item === 'string' && item.trim().startsWith('<');
                          
                          return isHtml ? (
                            <div
                              key={index}
                              className="prose prose-sm max-w-none"
                              dangerouslySetInnerHTML={{ __html: item }}
                            />
                          ) : (
                            <p key={index} className="leading-relaxed text-base">
                              {item}
                            </p>
                          );
                        })
                      ) : (
                        <p className="leading-relaxed text-base">
                          {chapter.content}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout> 
  );
}
