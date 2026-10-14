export function conLetra(total) {
  const U = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE', 'DIEZ', 'ONCE', 'DOCE', 'TRECE', 'CATORCE', 'QUINCE',
             'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO', 'DIECINUEVE', 'VEINTE', 'VEINTIÚN', 'VEINTIDÓS', 'VEINTITRÉS', 'VEINTICUATRO', 'VEINTICINCO',
             'VEINTISÉIS', 'VEINTISIETE', 'VEINTIOCHO', 'VEINTINUEVE'];
  const D = ['', '', '', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA'];
  const C = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS'];
  const decenas = n => n < 30 ? U[n] : D[Math.floor(n / 10)] + (n % 10 ? ' Y ' + U[n % 10] : '');
  const centenas = n => n === 100 ? 'CIEN' : (C[Math.floor(n / 100)] + ' ' + decenas(n % 100)).trim();
  const miles = n => {
    const m = Math.floor(n / 1000), r = n % 1000;
    const pm = m === 0 ? '' : m === 1 ? 'MIL' : centenas(m) + ' MIL';
    return (pm + ' ' + centenas(r)).trim();
  };
  const millones = n => {
    const m = Math.floor(n / 1e6), r = n % 1e6;
    const pm = m === 0 ? '' : m === 1 ? 'UN MILLÓN' : miles(m) + ' MILLONES';
    return (pm + ' ' + miles(r)).trim();
  };
  const enteros = Math.floor(total), cent = Math.round((total - enteros) * 100);
  const palabras = enteros === 0 ? 'CERO' : millones(enteros);
  const de = enteros >= 1e6 && enteros % 1e6 === 0 ? ' DE' : '';
  return `${palabras}${de} ${enteros === 1 ? 'PESO' : 'PESOS'} ${String(cent).padStart(2, '0')}/100 M.N.`;
}
