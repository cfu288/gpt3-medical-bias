import { useEffect, useState } from "react";
import { createDbWorker } from "sql.js-httpvfs";

const workerUrl = new URL(
  "sql.js-httpvfs/dist/sqlite.worker.js",
  import.meta.url
);
const wasmUrl = new URL("sql.js-httpvfs/dist/sql-wasm.wasm", import.meta.url);

async function load(query: string) {
  const worker = await createDbWorker(
    [
      {
        from: "inline",
        config: {
          serverMode: "full",
          url: "/database.sqlite3",
          // url: "/gpt3-medical-bias/database.sqlite3",
          requestChunkSize: 4096,
        },
      },
    ],
    workerUrl.toString(),
    wasmUrl.toString()
  );

  return await worker.db.query(query);
}

function App() {
  const [rows, setRows] = useState<QueryResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [query, setQuery] = useState<string>(
    "SELECT first_name, last_name, age, gender, race, chief_complaint, medications FROM Patient p JOIN History h ON h.patient_id = p.id LIMIT 5;"
  );
  const onSubmit = (e: any) => {
    e.preventDefault();
    load(e.target.search.value)
      .then((result) => {
        setRows(result as QueryResult[]);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    setLoading(true);
    load(query)
      .then((result) => {
        setRows(result as QueryResult[]);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <>
      <div className="px-4 sm:px-6 lg:px-8">
        <form onSubmit={onSubmit}>
          <label
            htmlFor="search"
            className="block text-sm font-medium leading-6 text-gray-900"
          >
            Query
          </label>
          <div className="relative mt-2 flex items-center">
            <input
              type="text"
              name="search"
              id="search"
              className="block w-full rounded-md border-0 py-1.5 pr-14 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <div className="absolute inset-y-0 right-0 flex py-1.5 pr-1.5">
              <kbd className="inline-flex items-center rounded border border-gray-200 px-1 font-sans text-xs text-gray-400">
                Enter
              </kbd>
            </div>
          </div>
        </form>
        <div>{loading && <div>Loading...</div>}</div>
        <div className="mt-8 flow-root">
          <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
              <table className="min-w-full divide-y divide-gray-300 table-fixed">
                <thead>
                  <tr>
                    {rows?.[0] &&
                      Object.keys(rows?.[0]).map((key) => (
                        <th
                          scope="col"
                          className="px-3 py-2 text-left text-sm font-semibold text-gray-900"
                        >
                          {key}
                        </th>
                      ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {rows.map((person) => (
                    <tr key={person.first_name + person.last_name}>
                      {Object.values(person).map((value) => (
                        <td className="px-3 py-2 text-sm text-gray-500">
                          {value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;

export interface QueryResult {
  id: any;
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  race: string;
  patient_id: number;
  chief_complaint: string;
  history_of_present_illness: string;
  review_of_symptoms__constitutional: string;
  review_of_symptoms__cardiovascular: string;
  review_of_symptoms__respiratory: string;
  review_of_symptoms__gi: string;
  review_of_symptoms__gu: string;
  review_of_symptoms__musculoskeletal: string;
  review_of_symptoms__skin: string;
  review_of_symptoms__neurologic: string;
  past_medical_history: string;
  medications: string;
  past_surgical_history: string;
  family_history: string;
  social_history: string;
  FOREIGN: any;
}
