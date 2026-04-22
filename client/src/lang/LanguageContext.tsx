import { useState, createContext } from "react";
import { IntlProvider } from "react-intl";
import French from "../lang/fr.json";
import Italian from "../lang/it.json";
import English from "../lang/en.json";
import German from "../lang/ger.json";
import { LANGUAGE } from "../appConstants";

type LanguageContextType = {
  setLanguage: (language: LANGUAGE) => void;
  language: LANGUAGE;
};

type GenericOpbject = { [key: string]: string };

export const LanguageContext = createContext<LanguageContextType>({
  setLanguage: () => {},
  language: LANGUAGE.DE,
});

type Props = { children: React.ReactElement | React.ReactElement[] };

export const LanguageProvider = ({ children }: Props) => {
  const [language, setLanguageState] = useState<LANGUAGE>(LANGUAGE.DE);
  const [messages, setMessages] = useState<GenericOpbject>(German);

  const setLanguage = (lang: LANGUAGE) => {
    if (lang === LANGUAGE.FR) {
      setLanguageState(LANGUAGE.FR);
      setMessages(French);
    }
    if (lang === LANGUAGE.IT) {
      setLanguageState(LANGUAGE.IT);
      setMessages(Italian);
    }
    if (lang === LANGUAGE.EN) {
      setLanguageState(LANGUAGE.EN);
      setMessages(English);
    }
    if (lang === LANGUAGE.DE) {
      setLanguageState(LANGUAGE.DE);
      setMessages(German);
    }
  };

  return (
    <LanguageContext.Provider value={{ setLanguage, language }}>
      <IntlProvider locale={language} messages={messages} defaultLocale="de">
        {children}
      </IntlProvider>
    </LanguageContext.Provider>
  );
};
