export const traduccionFinalidad: Record<string, string> = {
  '2112': 'Adquisición 1ª residencia',
  '2113': 'Adquisición 2ª residencia',
};

export const traduccionProvincia: Record<string, string> = {
  '01': 'Álava',
  '02': 'Albacete',
  '03': 'Alicante',
  '04': 'Almería',
  '05': 'Ávila',
  '06': 'Badajoz',
  '07': 'Islas Baleares',
  '08': 'Barcelona',
  '09': 'Burgos',
  '10': 'Cáceres',
  '11': 'Cádiz',
  '12': 'Castellón',
  '13': 'Ciudad Real',
  '14': 'Córdoba',
  '15': 'A Coruña',
  '16': 'Cuenca',
  '17': 'Girona',
  '18': 'Granada',
  '19': 'Guadalajara',
  '20': 'Guipúzcoa',
  '21': 'Huelva',
  '22': 'Huesca',
  '23': 'Jaén',
  '24': 'León',
  '25': 'Lleida',
  '26': 'La Rioja',
  '27': 'Lugo',
  '28': 'Madrid',
  '29': 'Málaga',
  '30': 'Murcia',
  '31': 'Navarra',
  '32': 'Ourense',
  '33': 'Asturias',
  '34': 'Palencia',
  '35': 'Las Palmas',
  '36': 'Pontevedra',
  '37': 'Salamanca',
  '38': 'Santa Cruz de Tenerife',
  '39': 'Cantabria',
  '40': 'Segovia',
  '41': 'Sevilla',
  '42': 'Soria',
  '43': 'Tarragona',
  '44': 'Teruel',
  '45': 'Toledo',
  '46': 'Valencia',
  '47': 'Valladolid',
  '48': 'Vizcaya',
  '49': 'Zamora',
  '50': 'Zaragoza',
  '51': 'Ceuta',
  '52': 'Melilla',
};

export const traduccionTipoInteres: Record<string, string> = {
  F: 'Fijo',
  V: 'Variable',
  M: 'Mixto',
};

export const traduccionSiNo: Record<string, string> = {
  S: 'Sí',
  N: 'No',
};

export const traducciontipoInmueble: Record<string, string> = {
  PSO: 'Piso',
  CHI: 'Chalet',
  CHA: 'Chalet Adosado',
  CAS: 'Casa',
};

export const traduccionEstadoInmueble: Record<string, string> = {
  P: 'EN PROYECTO',
  R: 'EN REHABILITACION',
  N: 'TERMINADO NUEVO',
  C: 'EN CONSTRUCCION',
  O: 'OBRA PARADA',
  T: 'TERMINADO USADO',
};

export const traduccionPersonaJuridica: Record<string, string> = {
  F: 'Persona Física',
  J: 'Persona Jurídica',
};

export const traduccionEstadoCivil: Record<string, string> = {
  C: 'Casado',
  D: 'Divorciado',
  P: 'Pareja de Hecho',
  S: 'Soltero',
  V: 'Viudo',
  H: 'Separado de Hecho',
  J: 'Separado Judicial',
};

export const traduccionRelacPrimerTitular: Record<string, string> = {
  '01': 'Padre/Madre',
  '02': 'Hermano/a',
  '03': 'Hijo/a',
  '04': 'Conyuge/Pareja',
};

export const traduccionSituacionLaboral: Record<string, string> = {
  A: 'Funcionario',
  B: 'Interino',
  '1': 'Fijo',
  '2': 'Temporal',
  '3': 'Temporero',
  '4': 'Autonomo',
  '5': 'Otros',
};

export const traduccionProfesion: Record<string, string> = {
  // Profesiones generales
  '1A': 'Gerente-Alto Cargo-Ejecutivo',
  '1B': 'Técnico Superior',
  '1C': 'Mando Intermedio',
  '1D': 'Administrativo',
  '1E': 'Representante Comisionista',
  '1F': 'Vendedor de Comercio',
  '1G': 'Encargado',
  '1H': 'Obrero Especializado',
  '1I': 'Obrero No Especializado',
  '1J': 'Profesor',
  '1K': 'Militar-Policía (No Municipal)',
  '1L': 'Policía Municipal',

  // Autónomos
  '4A': 'Médico',
  '4B': 'Abogado',
  '4C': 'Notario - Procurador',
  '4D': 'Arquitecto - Ingeniero',
  '4E': 'Periodista - Escritor - Traductor',
  '4F': 'Veterinario',
  '4G': 'Farmacéutico',
  '4H': 'Artista - Deportista',
  '4I': 'Otras Profesiones Liberales',
  '4J': 'No Profesionales Liberales',

  // Otros
  '5A': 'Religioso',
  '5B': 'Ama de casa',
  '5C': 'Rentista',
  '5D': 'Estudiante',
  '5E': 'Jubilado/Pensionista',
  '5F': 'Parado',
};

export const traduccionActEconomica: Record<string, string> = {
  '1A': 'AGRICULTURA Y CAZA',
  '1B': 'PESCA',
  '1C': 'ENERGIA Y AGUA',
  '1D': 'MINERIA',
  '1E': 'METALURGIA-SIDERURGIA',
  '1F': 'MAQUINARIA-INGENIERIA-MECANICA',
  '1G': 'FAB. ELECTRICA Y ELECTRONICA',
  '1H': 'CONSTRUCCION',
  '1I': 'ALIMENTACION Y TABACO',
  '1J': 'TEXTIL-MADERA-MUEBLE',
  '1K': 'PAPEL Y ARTES GRAFICAS',
  '1L': 'CUERO-PIEL-CALZADO-VESTIDO',
  '2A': 'ADMINISTRACION PUBLICA',
  '2B': 'MILITAR-POLICIA',
  '2C': 'DIPLOMATICOS-ORG.INTERNACIONAL',
  '2D': 'SANIDAD-SERVICIOS VETERINARIOS',
  '2E': 'ENSEÑANZA',
  '2F': 'BANCA-FINANCIERAS-SEGUROS',
  '2G': 'INFORMATICA-SERVICIOS',
  '2H': 'SERV. FINANCIEROS Y DE EMPRESA',
  '2I': 'SERV. DOMESTICOS O PERSONALES',
  '2J': 'COMERCIO-HOSTELERIA',
  '2K': 'REPARACION VEHICULOS',
  '2L': 'ALQUILER MUEBLES-INMUEBLES',
  '2M': 'PRENSA-RADIO-T.V.',
  '2N': 'ESPECTACULOS-DEPORTES',
  '2O': 'TRANSPORTE TERRESTRE',
  '2P': 'TRANSPORTE AEREO',
  '2Q': 'TR.MARITIMO-FLUVIAL-FERROVIAR',
  '2R': 'AGENCIAS DE VIAJE',
  '2S': 'COMUNICACIONES(CORREOS-CTNE)',
  '3A': 'ACTIVIDAD NO PRODUCTIVA',
};

export const traduccionSitViviendaHab: Record<string, string> = {
  '1': 'Sin vivienda habitual',
  '2': 'Libre de cargas',
  '3': 'Vivienda habitual en alquiler',
  '4': 'Propiedad hipotecada y mantiene la hipoteca',
  '5': 'Propiedad hipotecada pero se cancelará la hipoteca',
  '6': 'Domicilio de los padres o familia',
};

export const traduccionPais: Record<string, string> = {
  '011': 'España',
};

export const traduccionIndRelac: Record<string, string> = {
  T: 'Titular',
  A: 'Avalista',
  '': 'Otros',
};
