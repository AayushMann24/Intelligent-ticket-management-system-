import { useNavigate } from "react-router-dom";

export default function LandingPage() {

    const navigate = useNavigate();

    return (

        <div className="min-h-screen bg-slate-950 text-white">

            {/* Hero */}

            <section className="flex flex-col items-center justify-center h-screen text-center px-6">

                <h1 className="text-6xl font-extrabold mb-6">

                    Intelligent Ticket
                    <br />
                    Management System

                </h1>

                <p className="text-slate-400 text-xl max-w-3xl">

                    AI-powered ticket management platform with
                    intelligent classification, automatic priority
                    detection, smart technician assignment and
                    analytics dashboard.

                </p>

                <div className="flex gap-6 mt-10">

                    <button
                        onClick={() => navigate("/login")}
                        className="bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-xl text-lg"
                    >
                        Login
                    </button>

                    <button
                        onClick={() => navigate("/register")}
                        className="border border-slate-700 hover:bg-slate-900 px-8 py-4 rounded-xl text-lg"
                    >
                        Register
                    </button>

                </div>

            </section>

            {/* Features */}

            <section className="max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-8 px-8 pb-24">

                <Feature
                    icon="🤖"
                    title="AI Classification"
                    description="Automatically categorizes incoming tickets."
                />

                <Feature
                    icon="⚡"
                    title="Priority Detection"
                    description="AI predicts urgency and priority."
                />

                <Feature
                    icon="👨‍💻"
                    title="Smart Assignment"
                    description="Assigns tickets to the best technician."
                />

                <Feature
                    icon="📊"
                    title="Analytics"
                    description="Real-time dashboard and reporting."
                />

            </section>

        </div>

    );

}

function Feature({

    icon,

    title,

    description,

}: {

    icon: string;

    title: string;

    description: string;

}) {

    return (

        <div className="bg-slate-900 rounded-xl p-8">

            <div className="text-5xl">

                {icon}

            </div>

            <h2 className="text-2xl font-bold mt-5">

                {title}

            </h2>

            <p className="text-slate-400 mt-3">

                {description}

            </p>

        </div>

    );

}