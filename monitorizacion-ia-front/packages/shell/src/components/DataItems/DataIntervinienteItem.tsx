import { InputText } from '@internal-channels-components/input-text';
import { Accordion, AccordionTab } from '@internal-channels-components/accordion';

import { ContextItem, DataInterviniente, ItemType } from '../../domains/Context.domain';
import {
  traduccionProvincia,
  traduccionPersonaJuridica,
  traduccionSiNo,
  traduccionIndRelac,
  traduccionPais,
  traduccionEstadoCivil,
  traduccionSituacionLaboral,
  traduccionProfesion,
  traduccionActEconomica,
  traduccionSitViviendaHab,
  traduccionRelacPrimerTitular,
} from '../../domains/Traducciones.domain';

import { ItemContainer, SubseccionContainer } from './DataItem.styled';

export function DataIntervinienteItem({ item }: { item: ContextItem<ItemType> }) {
  const interviniente = item.data as DataInterviniente;

  // Helpers de formateo
  const s = (v?: string | null) => v ?? '';
  const n = (v?: number | null) => (v === null || v === undefined ? '' : String(v));

  // Alias cómodos
  const dp = interviniente.datosPersonalesYProfesionales;
  const dc = interviniente.datosContacto;
  const dir = dc?.direccion;
  const dv = interviniente.datosViviendaHabitual;
  const di = interviniente.datosIngresos;
  const se = interviniente.datosSituacionEconomica;

  // Derivados
  const nombreCompleto = `${s(dp?.nombre)} ${s(dp?.apellido1)} ${s(dp?.apellido2)}`.trim();
  const direccionCompleta = dir
    ? `${s(dir.tipoVia)} ${s(dir.domicilio)} ${s(dir.numero)} ${s(dir.portal)} ${s(dir.bloque)} ${s(dir.escalera)} ${s(
        dir.puerta,
      )} ${s(dir.planta)} ${s(dir.parcela)} ${s(dir.km)} ${s(dir.poblacion)} (${s(dir.codPostal)}) ${
        traduccionProvincia[s(dir.codProvincia)]
      }`
        .replace(/\s+/g, ' ')
        .trim()
    : '';

  return (
    <SubseccionContainer>
      <Accordion>
        {/* 1. Datos personales y profesionales */}
        <AccordionTab header="1. Datos personales y profesionales">
          <ItemContainer>
            <InputText disabled size="small" label="Nombre completo" value={nombreCompleto} />
            <InputText disabled size="small" label="NIF" value={s(dp?.nif)} />
            <InputText disabled size="small" label="Fecha de nacimiento" value={s(dp?.fechaNacimiento)} />
            <InputText disabled size="small" label="Fecha antigüedad empresa" value={s(dp?.fechaAntEmpresa)} />
            <InputText disabled size="small" label="Sexo" value={s(dp?.sexo)} />
            <InputText
              disabled
              size="small"
              label="Ind. persona jurídica"
              value={traduccionPersonaJuridica[s(dp?.indPerJur)]}
            />
            <InputText disabled size="small" label="Código cliente" value={s(dp?.codCliente)} />
            <InputText
              disabled
              size="small"
              label="Indicador relación"
              value={traduccionIndRelac[s(dp?.rolInterviniente)]}
            />
            <InputText disabled size="small" label="Comunidad/Unidad familiar" value={n(dp?.comUniFamiliar)} />
            <InputText disabled size="small" label="Residente" value={traduccionSiNo[s(dp?.indResidente)]} />
            <InputText disabled size="small" label="Nacionalidad" value={traduccionPais[s(dp?.nacionalidad)]} />
            <InputText disabled size="small" label="Estado civil" value={traduccionEstadoCivil[s(dp?.estadoCivil)]} />
            <InputText
              disabled
              size="small"
              label="Relación 1er titular"
              value={traduccionRelacPrimerTitular[s(dp?.relacPrimerTitular)]}
            />
            <InputText
              disabled
              size="small"
              label="Situación laboral"
              value={traduccionSituacionLaboral[s(dp?.sitLaboral)]}
            />
            <InputText disabled size="small" label="Profesión" value={traduccionProfesion[s(dp?.profesion)]} />
            <InputText
              disabled
              size="small"
              label="Actividad económica"
              value={traduccionActEconomica[s(dp?.actEconomica)]}
            />
            <InputText disabled size="small" label="CNAE" value={s(dp?.cnae)} />
          </ItemContainer>
        </AccordionTab>

        {/* 2. Datos de contacto */}
        <AccordionTab header="2. Datos de contacto">
          <ItemContainer>
            <InputText disabled size="small" label="Email" value={s(dc?.email)} />
            <InputText disabled size="small" label="Móvil" value={`${s(dc?.prefijo)} ${s(dc?.movil)}`.trim()} />
            <InputText disabled size="small" label="País teléfono" value={traduccionPais[s(dc?.paisTelefono)]} />
            <InputText disabled size="small" label="Dirección completa" value={direccionCompleta} />
          </ItemContainer>
        </AccordionTab>

        {/* 3. Vivienda habitual */}
        <AccordionTab header="3. Vivienda habitual">
          <ItemContainer>
            <InputText
              disabled
              size="small"
              label="Situación vivienda habitual"
              value={traduccionSitViviendaHab[s(dv?.sitViviendaHab)]}
            />
            <InputText disabled size="small" label="Valor vivienda" value={n(dv?.valorVivienda)} />
            <InputText disabled size="small" label="Gastos alquiler" value={n(dv?.gastosAlquiler)} />
            <InputText disabled size="small" label="Cargas vivienda" value={n(dv?.cargasVivienda)} />
          </ItemContainer>
        </AccordionTab>

        {/* 4. Ingresos */}
        <AccordionTab header="4. Ingresos">
          <ItemContainer>
            <InputText disabled size="small" label="Ingresos fijos" value={n(di?.ingresoFijos)} />
            <InputText disabled size="small" label="Ingresos variables" value={n(di?.ingresosVar)} />
            <InputText disabled size="small" label="Otros ingresos" value={n(di?.ingresosOtros)} />
          </ItemContainer>
        </AccordionTab>

        {/* 5. Situación económica */}
        <AccordionTab header="5. Situación económica">
          <ItemContainer>
            <InputText
              disabled
              size="small"
              label="Comparten gastos/ingresos"
              value={traduccionSiNo[s(se?.indCompGtosIngr)]}
            />
            <InputText disabled size="small" label="NIF acompañante" value={s(se?.nifCompGtosIngr)} />
            <InputText
              disabled
              size="small"
              label="Ctas. en otras entidades"
              value={traduccionSiNo[s(se?.ctaOtrasEntidades)]}
            />
            <InputText disabled size="small" label="Posee inmueble" value={traduccionSiNo[s(se?.indInmueble)]} />
            <InputText disabled size="small" label="Deudas en OOEE" value={traduccionSiNo[s(se?.indDeudasOOEE)]} />
            <InputText disabled size="small" label="Cuotas OOEE" value={n(se?.cuotasOOEE)} />
          </ItemContainer>
        </AccordionTab>

        {/* 6. Datos generales */}
        <AccordionTab header="6. Datos generales">
          <ItemContainer>
            <InputText
              disabled
              size="small"
              label="Consumidor"
              value={traduccionSiNo[s(interviniente.infConsumidor)]}
            />
            <InputText
              disabled
              size="small"
              label="País de residencia"
              value={traduccionPais[s(interviniente.paisResidencia)]}
            />
          </ItemContainer>
        </AccordionTab>
      </Accordion>
    </SubseccionContainer>
  );
}
