export type ItemType =
  | 'DataCliente'
  | 'DataGestor'
  | 'DataPreeval'
  | 'DataOperacion'
  | 'DataInterviniente'
  | 'RecomendacionHipoteca'
  | 'DataMuestraInteres'
  | string
  | null;

// Instancias
export type ItemDataMap = {
  DataCliente: DataCliente;
  DataGestor: DataGestor;
  DataInterviniente: DataInterviniente;
  DataOperacion: DataOperacion;
  DataPreeval: DataPreeval;
  RecomendacionHipoteca: RecomendacionHipoteca;
  DataMuestraInteres: DataMuestraInteres;
  // etc.
};

// Constructores
export type ItemDataClassMap = {
  DataCliente: typeof DataCliente;
  DataGestor: typeof DataGestor;
  DataInterviniente: typeof DataInterviniente;
  DataOperacion: typeof DataOperacion;
  DataPreeval: typeof DataPreeval;
  RecomendacionHipoteca: typeof RecomendacionHipoteca;
  DataMuestraInteres: typeof DataMuestraInteres;
  // etc.
};

export class ContextItem<T extends ItemType | null = null> {
  id: string | null;
  name: string | null;
  tab: string | null;
  llmHeader: string | null;
  itemType: T | null;
  data: T extends keyof ItemDataMap ? ItemDataMap[T] : any;

  constructor(raw: {
    id: string | null;
    name: string | null;
    tab: string | null;
    llm_header: string | null;
    item_type: T | null;
    data: any;
  }) {
    this.id = raw.id;
    this.name = raw.name;
    this.itemType = raw.item_type;
    this.tab = raw.tab;
    this.llmHeader = raw.llm_header;

    const DataClass = raw.item_type && dataClassMap[raw.item_type as keyof ItemDataClassMap];
    this.data = DataClass ? new DataClass(raw.data) : raw.data;
  }
}

export class DataCliente {
  nif: string;
  claper: string;
  fechaNacimiento: string;
  nombreCompleto: string;
  email: string;
  telefono: string;
  direccion: string;

  constructor(data: Partial<DataCliente>) {
    this.nif = data.nif ?? '';
    this.claper = data.claper ?? '';
    this.fechaNacimiento = data.fechaNacimiento ?? '';
    this.nombreCompleto = data.nombreCompleto ?? '';
    this.email = data.email ?? '';
    this.telefono = data.telefono ?? '';
    this.direccion = data.direccion ?? '';
  }
}

export class DataGestor {
  codigo: string;
  centro: string;

  constructor(data: Partial<DataGestor>) {
    this.codigo = data.codigo ?? '';
    this.centro = data.centro ?? '';
  }
}

export class DataInterviniente {
  datosPersonalesYProfesionales: {
    codCliente: string;
    rolInterviniente: string;
    nif: string;
    nombre: string;
    apellido1: string;
    apellido2: string;
    indPerJur: string;
    fechaNacimiento: string;
    fechaAntEmpresa: string;
    sexo: string;
    comUniFamiliar: number | null;
    indResidente: string;
    nacionalidad: string;
    estadoCivil: string;
    relacPrimerTitular: string;
    sitLaboral: string | null;
    profesion: string | null;
    actEconomica: string | null;
    cnae: string;
  } | null;

  datosViviendaHabitual: {
    sitViviendaHab: string;
    valorVivienda: number;
    gastosAlquiler: number;
    cargasVivienda: number;
  } | null;

  datosIngresos: {
    ingresoFijos: number;
    ingresosVar: number;
    ingresosOtros: number;
  } | null;

  datosSituacionEconomica: {
    indCompGtosIngr: string;
    nifCompGtosIngr: string;
    ctaOtrasEntidades: string;
    indInmueble: string;
    indDeudasOOEE: string;
    cuotasOOEE: number;
  } | null;

  datosContacto: {
    email: string;
    prefijo: string;
    movil: string | null;
    paisTelefono: string;
    direccion: {
      tipoVia: string;
      puerta: string;
      portal: string;
      poblacion: string;
      planta: string;
      numero: string;
      domicilio: string;
      restoDireccion: string;
      codProvincia: string;
      codPostal: string;
      codPais: string;
      bloque: string;
      escalera: string;
      km: string;
      parcela: string;
    };
  } | null;

  infConsumidor: string;
  paisResidencia: string;

  constructor(data: any) {
    // datos_personales_y_profesionales
    const personales = data.datos_personales_y_profesionales ?? {};
    this.datosPersonalesYProfesionales = {
      codCliente: personales.codCliente ?? '',
      rolInterviniente: personales.rolInterviniente ?? '',
      nif: personales.nif ?? '',
      nombre: personales.nombre ?? '',
      apellido1: personales.apellido1 ?? '',
      apellido2: personales.apellido2 ?? '',
      indPerJur: personales.indPerJur ?? '',
      fechaNacimiento: personales.fechaNacimiento ?? '',
      fechaAntEmpresa: personales.fechaAntEmpresa ?? '',
      sexo: personales.sexo ?? '',
      comUniFamiliar: personales.comUniFamiliar ?? null,
      indResidente: personales.indResidente ?? '',
      nacionalidad: personales.nacionalidad ?? '',
      estadoCivil: personales.estadoCivil ?? '',
      relacPrimerTitular: personales.relacPrimerTitular ?? '',
      sitLaboral: personales.sitLaboral ?? null,
      profesion: personales.profesion ?? null,
      actEconomica: personales.actEconomica ?? null,
      cnae: personales.cnae ?? '',
    };

    // datos_vivienda_habitual
    const vivienda = data.datos_vivienda_habitual ?? {};
    this.datosViviendaHabitual = {
      sitViviendaHab: vivienda.sitViviendaHab ?? '',
      valorVivienda: vivienda.valorVivienda,
      gastosAlquiler: vivienda.gastosAlquiler,
      cargasVivienda: vivienda.cargasVivienda,
    };

    // datos_ingresos
    const ingresos = data.datos_ingresos ?? {};
    this.datosIngresos = {
      ingresoFijos: ingresos.ingresoFijos,
      ingresosVar: ingresos.ingresosVar,
      ingresosOtros: ingresos.ingresosOtros,
    };

    // datos_situacion_economica
    const situacion = data.datos_situacion_economica ?? {};
    this.datosSituacionEconomica = {
      indCompGtosIngr: situacion.indCompGtosIngr ?? '',
      nifCompGtosIngr: situacion.nifCompGtosIngr ?? '',
      ctaOtrasEntidades: situacion.ctaOtrasEntidades ?? '',
      indInmueble: situacion.indInmueble ?? '',
      indDeudasOOEE: situacion.indDeudasOOEE ?? '',
      cuotasOOEE: situacion.cuotasOOEE,
    };

    // datos_contacto
    const contacto = data.datos_contacto ?? {};
    const direccion = contacto.direccion ?? {};
    this.datosContacto = {
      email: contacto.email ?? '',
      prefijo: contacto.prefijo ?? '',
      movil: contacto.movil ?? '',
      paisTelefono: contacto.paisTelefono ?? '',
      direccion: {
        tipoVia: direccion.tipoVia ?? '',
        puerta: direccion.puerta ?? '',
        portal: direccion.portal ?? '',
        poblacion: direccion.poblacion ?? '',
        planta: direccion.planta ?? '',
        numero: direccion.numero ?? '',
        domicilio: direccion.domicilio ?? '',
        restoDireccion: direccion.restoDireccion ?? '',
        codProvincia: direccion.codProvincia ?? '',
        codPostal: direccion.codPostal ?? '',
        codPais: direccion.codPais ?? '',
        bloque: direccion.bloque ?? '',
        escalera: direccion.escalera ?? '',
        km: direccion.km ?? '',
        parcela: direccion.parcela ?? '',
      },
    };

    this.infConsumidor = data.infConsumidor ?? '';
    this.paisResidencia = data.paisResidencia ?? '';
  }
}

export class DataOperacion {
  subproducto: string;
  plazoTotalU: string;
  plazoTotal: number;
  indUsoResidencial: string;
  indTipoIntSS: string;
  importeSolicitado: number;
  finalidad: string;

  constructor(data: any) {
    this.subproducto = data.subproducto ?? '';
    this.plazoTotalU = data.plazoTotalU ?? '';
    this.plazoTotal = data.plazoTotal;
    this.indUsoResidencial = data.indUsoResidencial ?? '';
    this.indTipoIntSS = data.indTipoIntSS ?? '';
    this.importeSolicitado = data.importeSolicitado;
    this.finalidad = data.finalidad ?? '';
  }
}

export class DataPreeval {
  valorTasa: number;
  precioVivienda: number;
  importeTotalInversion: number;
  tipoInmu: string;
  provincia: string;
  hipVvdaHab: string;
  codEstadoInmu: string;

  constructor(data: any) {
    this.valorTasa = data.valorTasa;
    this.precioVivienda = data.precioVivienda;
    this.importeTotalInversion = data.importeTotalInversion;
    this.tipoInmu = data.tipoInmu ?? '';
    this.provincia = data.provincia ?? '';
    this.hipVvdaHab = data.hipVvdaHab ?? '';
    this.codEstadoInmu = data.codEstadoInmu ?? '';
  }
}

export class DataProducto {
  nombreProducto: string;
  codigoProducto: {
    comercial: string;
    administrativo: string;
  };
  descripcionProducto: string;
  publicoObjetivo: string;
  condicionesFinancieras: Record<string, string>;
  tarifas: {
    tipoDeInteresFijoConBonificacionPorVinculacion: string;
    tiposInteres: Record<string, string>;
    comisiones: Record<string, string>;
  };
  bloquesDeBonificacionPorMantenimientoYContratacionDeProductos: {
    producto: string;
    bonificacion: string;
  }[];
  bonificacionMaxima: string;
  periodicidadDeRevision: string;
  atribucionesEnCondicionesFinancieras: string;
  atribucionesEnConcesionDeOperaciones: string;
  consideracionesGenerales: string;
  argumentarioComercial: string;

  constructor(data: any) {
    this.nombreProducto = data.nombre_producto ?? '';
    this.codigoProducto = data.codigo_producto ?? { comercial: '', administrativo: '' };
    this.descripcionProducto = data.descripcion_producto ?? '';
    this.publicoObjetivo = data.publico_objetivo ?? '';
    this.condicionesFinancieras = data.condiciones_financieras ?? {};
    this.tarifas = data.tarifas ?? {
      tipoDeInteresFijoConBonificacionPorVinculacion: '',
      tiposInteres: {},
      comisiones: {},
    };
    this.bloquesDeBonificacionPorMantenimientoYContratacionDeProductos =
      data.bloques_de_bonificacion_por_mantenimiento_y_contratacion_de_productos ?? [];
    this.bonificacionMaxima = data.bonificacion_maxima ?? '';
    this.periodicidadDeRevision = data.periodicidad_de_revision ?? '';
    this.atribucionesEnCondicionesFinancieras = data.atribuciones_en_condiciones_financieras ?? '';
    this.atribucionesEnConcesionDeOperaciones = data.atribuciones_en_concesion_de_operaciones ?? '';
    this.consideracionesGenerales = data.consideraciones_generales ?? '';
    this.argumentarioComercial = data.argumentario_comercial ?? '';
  }
}

export class RecomendacionHipoteca {
  tipoInteres: string[];
  ingresos: number;
  edad: number;
  certificacionEnergeticaVivienda: string;
  timestamp: string;
  resultadoRecomendacion: DataProducto[];

  constructor(data: any) {
    this.tipoInteres = data.tipo_interes ?? [];
    this.ingresos = data.ingresos;
    this.edad = data.edad;
    this.certificacionEnergeticaVivienda = data.certificacion_energetica_vivienda ?? '';
    this.timestamp = data.timestamp ?? '';

    try {
      this.resultadoRecomendacion = data.resultado_recomendacion.map((p: any) => new DataProducto(p));
    } catch {
      this.resultadoRecomendacion = [];
    }
  }
}

export class NumExpeSG {
  anyo: string;
  centro: string;
  idExpe: string;

  constructor(data: any) {
    this.anyo = data.anyo ?? '';
    this.centro = data.centro ?? '';
    this.idExpe = data.idExpe ?? '';
  }
}

export class GrExpeActvo {
  numExpePdte: string;
  nifPdte: string;
  faseExpediente: string;

  constructor(data: any) {
    this.numExpePdte = data.numExpePdte ?? '';
    this.nifPdte = data.nifPdte ?? '';
    this.faseExpediente = data.faseExpediente ?? '';
  }
}

export class TitularAlta {
  nifAlta: string;
  claperAlta: string;

  constructor(data: any) {
    this.nifAlta = data.nifAlta ?? '';
    this.claperAlta = data.claperAlta ?? '';
  }
}

export class ConceptoPricing {
  conceptoSCF: string;
  desConceptoSCF: string;
  tipoDatoSCF: string;
  datoSCF: string;

  constructor(data: any) {
    this.conceptoSCF = data.conceptoSCF ?? '';
    this.desConceptoSCF = data.desConceptoSCF ?? '';
    this.tipoDatoSCF = data.tipoDatoSCF ?? '';
    this.datoSCF = data.datoSCF ?? '';
  }
}

export class DataMuestraInteres {
  resultadoLogOperacional: string;
  resultadoMuestraInteres: ResultadoMuestraInteres;

  constructor(data: any) {
    this.resultadoLogOperacional = data.resultado_log_operacional ?? '';
    this.resultadoMuestraInteres = new ResultadoMuestraInteres(data.resultado_muestra_interes ?? data);
  }
}

export class ResultadoMuestraInteres {
  documento: string;
  numExpeSG: NumExpeSG;
  grExpeActvos: GrExpeActvo[];
  recoDecision: string;
  descRecoDecision: string;
  impPerdEspe: string;
  porcentPd: string;
  porcentLgd: string;
  codResultadoSS: string;
  resultadoPreEval: string;
  motivoResultadoSS: string;
  porcNivelRsgo: string;
  titularesAlta: TitularAlta[];
  reglas: any[];
  conceptosPricing: ConceptoPricing[];
  cuotaPrimerPeriodo: string;
  cuotaRestoPeriodo: string;
  cuotaRestoPeriodMixta: string;
  tipoIntPrimerPeriodo: string;
  tipoIndRestoPeriodo: string;
  tipoIndRestoPeriodMixt: string;
  tae: string;
  diferencialCont: string;
  importeTotalAdeud: string;
  cuotaPrimerPeriodoSinBonif: string;
  cuotaRestoPeriodSinBonif: string;
  cuotaRestoPeriodMixtSinBonif: string;
  tipoIntPrimerPeriodSinBonif: string;
  tipoIntRestPeriodoSinBonif: string;
  tipoIndRestoMixtSinBonif: string;
  taeSinBonif: string;
  diferencialContSinBonif: string;
  importeTotalAdeuSinBonif: string;
  bonificacionMax: string;
  campanya: string;
  periodoTipInicial: string;
  periodoRevision: string;
  periodoTramoFijoMixt: string;

  constructor(data: any) {
    this.documento = data.documento ?? '';
    this.numExpeSG = new NumExpeSG(data.numExpeSG);
    this.grExpeActvos = (data.grExpeActvos ?? []).map((item: any) => new GrExpeActvo(item));
    this.recoDecision = data.recoDecision ?? '';
    this.descRecoDecision = data.descRecoDecision ?? '';
    this.impPerdEspe = data.impPerdEspe ?? '';
    this.porcentPd = data.porcentPd ?? '';
    this.porcentLgd = data.porcentLgd ?? '';
    this.codResultadoSS = data.codResultadoSS ?? '';
    this.resultadoPreEval = data.resultadoPreEval ?? '';
    this.motivoResultadoSS = data.motivoResultadoSS ?? '';
    this.porcNivelRsgo = data.porcNivelRsgo ?? '';
    this.titularesAlta = (data.titularesAlta ?? []).map((item: any) => new TitularAlta(item));
    this.reglas = data.reglas ?? [];
    this.conceptosPricing = (data.conceptosPricing ?? []).map((item: any) => new ConceptoPricing(item));
    this.cuotaPrimerPeriodo = data.cuotaPrimerPeriodo ?? '';
    this.cuotaRestoPeriodo = data.cuotaRestoPeriodo ?? '';
    this.cuotaRestoPeriodMixta = data.cuotaRestoPeriodMixta ?? '';
    this.tipoIntPrimerPeriodo = data.tipoIntPrimerPeriodo ?? '';
    this.tipoIndRestoPeriodo = data.tipoIndRestoPeriodo ?? '';
    this.tipoIndRestoPeriodMixt = data.tipoIndRestoPeriodMixt ?? '';
    this.tae = data.tae ?? '';
    this.diferencialCont = data.diferencialCont ?? '';
    this.importeTotalAdeud = data.importeTotalAdeud ?? '';
    this.cuotaPrimerPeriodoSinBonif = data.cuotaPrimerPeriodoSinBonif ?? '';
    this.cuotaRestoPeriodSinBonif = data.cuotaRestoPeriodSinBonif ?? '';
    this.cuotaRestoPeriodMixtSinBonif = data.cuotaRestoPeriodMixtSinBonif ?? '';
    this.tipoIntPrimerPeriodSinBonif = data.tipoIntPrimerPeriodSinBonif ?? '';
    this.tipoIntRestPeriodoSinBonif = data.tipoIntRestPeriodoSinBonif ?? '';
    this.tipoIndRestoMixtSinBonif = data.tipoIndRestoMixtSinBonif ?? '';
    this.taeSinBonif = data.taeSinBonif ?? '';
    this.diferencialContSinBonif = data.diferencialContSinBonif ?? '';
    this.importeTotalAdeuSinBonif = data.importeTotalAdeuSinBonif ?? '';
    this.bonificacionMax = data.bonificacionMax ?? '';
    this.campanya = data.campanya ?? '';
    this.periodoTipInicial = data.periodoTipInicial ?? '';
    this.periodoRevision = data.periodoRevision ?? '';
    this.periodoTramoFijoMixt = data.periodoTramoFijoMixt ?? '';
  }
}

export const dataClassMap: ItemDataClassMap = {
  DataCliente: DataCliente,
  DataGestor: DataGestor,
  DataInterviniente: DataInterviniente,
  DataOperacion: DataOperacion,
  DataPreeval: DataPreeval,
  RecomendacionHipoteca: RecomendacionHipoteca,
  DataMuestraInteres: DataMuestraInteres,
  // etc.
};
