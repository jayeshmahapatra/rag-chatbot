import React from 'react';

export const Footer: React.FC = () => {
    return (
        <footer className="flex flex-col items-center mt-4 w-full">
            <div className="flex items-center">
                <a
                    href="https://github.com/jayeshmahapatra/rag-chatbot"
                    target="_blank"
                    className="text-white flex items-center mr-4"
                >
                    <img src="/images/github-mark.svg" className="h-4 mr-1" alt="GitHub Mark" />
                    <span>View Source</span>
                </a>
            </div>
            <div className="flex flex-row items-center justify-between w-full">
                <a
                    href="https://jayeshmahapatra.github.io"
                    target="_blank"
                    className="text-white flex items-center mr-20 ml-20"
                >   
                    <img src="/images/notebook.svg" className="svg-icon mr-1" alt="Blog Mark" />
                    <span>Blog</span>
                </a>
                <a
                    href="https://github.com/jayeshmahapatra"
                    target="_blank"
                    className="text-white flex items-center"
                >
                    <svg className='svg-icon mr-1'>
                        <use xlinkHref="/images/minima-social-icons.svg#github"/>
                    </svg>
                    <span>GitHub</span>
                </a>
                <a
                    href="https://www.linkedin.com/in/jayeshmahapatra"
                    target="_blank"
                    className="text-white flex items-center mr-20 ml-20"
                >
                    <svg className='svg-icon mr-1'>
                        <use xlinkHref="/images/minima-social-icons.svg#linkedin"/>
                    </svg>
                    <span>LinkedIn</span>
                </a>
            </div>
        </footer>
    );
};

