\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{fizykalab}

\LoadClass{article}

% Czcionki i język polski
\RequirePackage[utf8]{inputenc}
\RequirePackage[polish]{babel}
\RequirePackage[T1]{fontenc}

% Pozycjonowanie rzeczy
\RequirePackage{adjustbox}
\RequirePackage{float}
\RequirePackage{wrapfig}

% Tabelki
\RequirePackage{multicol}
\RequirePackage{multirow}
\RequirePackage{booktabs}
\RequirePackage{tabularx}
\RequirePackage{longtable}

% Grafika
\RequirePackage{graphicx}

% Pisane rzeczy
\RequirePackage{caption}
\RequirePackage{listings}
\RequirePackage{comment}
\RequirePackage[colorlinks, linkcolor=black]{hyperref}

% Matematyka
\RequirePackage{amsmath}

% Fizyka
\RequirePackage{siunitx}

% Definicje do tabelki

\newcommand\wydzial[1]{\def\@wydzial{#1}}
\newcommand\autorjeden[1]{\def\@autorjeden{#1}}
\newcommand\autordwa[1]{\def\@autordwa{#1}}
\newcommand\rok[1]{\def\@rok{#1}}
\newcommand\grupa[1]{\def\@grupa{#1}}
\newcommand\zespol[1]{\def\@zespol{#1}}
\newcommand\temat[1]{\def\@temat{#1}}
\newcommand\nrcwiczenia[1]{\def\@nrcwiczenia{#1}}
\newcommand\datawykonania[1]{\def\@datawykonania{#1}}
\newcommand\dataoddaniajeden[1]{\def\@dataoddaniajeden{#1}}
\newcommand\zwrotdopoprawy[1]{\def\@zwrotdopoprawy{#1}}
\newcommand\dataoddaniadwa[1]{\def\@dataoddaniadwa{#1}}
\newcommand\datazaliczenia[1]{\def\@datazaliczenia{#1}}

% Tabelka

\renewcommand\maketitle{
\begin{table}[H]
\begin{adjustbox}{center}
\begin{tabular}{|l|l|l|l|l|l|}
\hline
 Wydział& \multicolumn{2}{l|}{Imię i nazwisko} & Rok & Grupa & Zespół  \\ 
 \multicolumn{1}{|c|}{\multirow{2}{*}{\textbf{\@wydzial}}} &\multicolumn{2}{l|}{\textbf{\@autorjeden}} & \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@rok}}} & \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@grupa}}} & \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@zespol}}}\\ 
 &\multicolumn{2}{l|}{\textbf{\@autordwa}}   &&&\\ \hline
 \multicolumn{1}{|c|}{\textbf{PRACOWNIA}} & \multicolumn{4}{l|}{Temat:} & Nr ćwiczenia  \\ 
 \multicolumn{1}{|c|}{\textbf{FIZYCZNA}} & \multicolumn{4}{l|}{\textbf{\@temat}} & \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@nrcwiczenia}}}\\ 
 \multicolumn{1}{|c|}{\textbf{WFiIS AGH}} & \multicolumn{4}{l|}{} & \\ \hline
 Data wykonania & Data oddania      & Zwrot do popr.      & Data oddania      & Data zaliczenia & OCENA\\
 \multicolumn{1}{|c|}{\multirow{2}{*}{\textbf{\@datawykonania}}} & \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@dataoddaniajeden}}} &
 \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@zwrotdopoprawy}}} &
 \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@dataoddaniadwa}}} &
 \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\@datazaliczenia}}} & \\
 & & & & & \\ \hline
\end{tabular}
\end{adjustbox}
\end{table}
}
