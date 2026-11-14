import React, { useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { DayPicker } from "react-day-picker";
import { ptBR } from "react-day-picker/locale";
import { ChevronDown } from "lucide-react";
import "react-day-picker/style.css";

const paraData = (valor) =>
  valor ? new Date(`${valor}T00:00:00`) : undefined;

const paraIsoLocal = (data) => {
  if (!data) return "";
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, "0");
  const dia = String(data.getDate()).padStart(2, "0");
  return `${ano}-${mes}-${dia}`;
};

const textoData = (valor) => {
  if (!valor) return "—";
  const [ano, mes, dia] = valor.split("-");
  return `${dia}/${mes}/${ano}`;
};

const estiloCalendarioRose = {
  "--rdp-accent-color": "#BE123C",
  "--rdp-accent-background-color": "#FFE4E6",
  "--rdp-range_middle-background-color": "#FFF1F2",
  "--rdp-range_middle-color": "#172033",
  "--rdp-range_start-date-background-color": "#BE123C",
  "--rdp-range_end-date-background-color": "#BE123C",
  "--rdp-range_start-color": "#FFFFFF",
  "--rdp-range_end-color": "#FFFFFF",
  "--rdp-selected-border": "2px solid #BE123C",
  "--rdp-day_button-border-radius": "8px",
};

export function SeletorPeriodoCalendario({
  inicio = "",
  fim = "",
  rotulo,
  disabled = false,
  onChange,
}) {
  const [aberto, definirAberto] = useState(false);
  const [posicao, definirPosicao] = useState({ left: 0, top: 0 });
  const [rascunho, definirRascunho] = useState(undefined);
  const [aguardandoFim, definirAguardandoFim] = useState(false);
  const selecionadoConfirmado = useMemo(
    () => ({ from: paraData(inicio), to: paraData(fim) }),
    [inicio, fim],
  );
  const selecionado = rascunho ?? selecionadoConfirmado;

  const selecionar = (periodo) => {
    if (!aguardandoFim) {
      definirRascunho({ from: periodo?.from ?? periodo?.to, to: undefined });
      definirAguardandoFim(true);
      return;
    }
    const novoInicio = paraIsoLocal(periodo?.from);
    const novoFim = paraIsoLocal(periodo?.to);
    onChange(novoInicio, novoFim);
    definirRascunho(undefined);
    definirAguardandoFim(false);
    definirAberto(false);
  };

  const alternarCalendario = (evento) => {
    if (aberto) {
      definirAberto(false);
      definirRascunho(undefined);
      definirAguardandoFim(false);
      return;
    }
    const limite = evento.currentTarget.getBoundingClientRect();
    definirPosicao({
      left: Math.max(16, Math.min(limite.left, window.innerWidth - 336)),
      top: Math.max(16, Math.min(limite.bottom + 8, window.innerHeight - 396)),
    });
    definirAberto(true);
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
      }}
    >
      <button
        type="button"
        aria-label={`Selecionar período de ${rotulo}`}
        aria-expanded={aberto}
        disabled={disabled}
        onClick={alternarCalendario}
        className="mira-date-trigger"
        style={{
          alignItems: "center",
          background: "#FFFFFF",
          border: "1px solid #DCE0E9",
          borderRadius: "8px",
          color: "#172033",
          cursor: disabled ? "not-allowed" : "pointer",
          display: "flex",
          font: "inherit",
          justifyContent: "space-between",
          minHeight: "2.5rem",
          padding: "0 0.75rem",
          textAlign: "left",
          width: "100%",
        }}
      >
        <span style={{ color: "#626C7D", fontSize: "0.75rem", lineHeight: 1.5 }}>
          De {textoData(inicio)} &nbsp; Até {textoData(fim)}
        </span>
        <ChevronDown aria-hidden="true" size={16} style={{ color: "#626C7D", flexShrink: 0 }} />
      </button>
      {aberto &&
        createPortal(
        <div
          role="dialog"
          aria-label={`Calendário de ${rotulo}`}
          style={{
            ...estiloCalendarioRose,
            background: "#FFFFFF",
            border: "1px solid #E6E8F0",
            borderRadius: "14px",
            boxShadow: "0 12px 30px rgba(35, 25, 45, 0.16)",
            marginTop: "0.5rem",
            padding: "0.75rem",
            width: "20rem",
            maxWidth: "calc(100vw - 2rem)",
            maxHeight: "calc(100vh - 2rem)",
            overflowY: "auto",
            fontFamily: '"Plus Jakarta Sans", "Segoe UI", sans-serif',
            color: "#172033",
            left: posicao.left,
            position: "fixed",
            top: posicao.top,
            zIndex: 1000,
          }}
        >
          <DayPicker
            locale={ptBR}
            mode="range"
            selected={selecionado}
            onSelect={selecionar}
            showOutsideDays
            style={estiloCalendarioRose}
          />
        </div>
        ,
        document.body,
      )}
    </div>
  );
}
