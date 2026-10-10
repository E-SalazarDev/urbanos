import { Text, type TextProps } from 'react-native';

import { tipografia, useTema, type Variante } from '../theme';

type Props = TextProps & {
  variante?: Variante;
  suave?: boolean; 
  color?: string;
};

export function Texto({ variante = 'cuerpo', suave, color, style, ...resto }: Props) {
  const { paleta } = useTema();
  return (
    <Text
      {...resto}
      style={[tipografia[variante], { color: color ?? (suave ? paleta.textoSuave : paleta.texto) }, style]}
    />
  );
}
