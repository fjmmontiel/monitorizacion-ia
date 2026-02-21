/* istanbul ignore file */
import React, { useEffect, useState } from 'react';
import { Accordion, AccordionTab } from '@internal-channels-components/accordion';
import { Icon } from '@internal-channels-components/icon';
import { IconButton } from '@internal-channels-components/icon-button';
import { Dialog } from '@internal-channels-components/dialog';
import { Button } from '@internal-channels-components/button';
import { InputText } from '@internal-channels-components/input-text';
import { FileUpload } from '@internal-channels-components/file-upload';
import { Dropdown } from '@internal-channels-components/dropdown';

import contextService from '../../services/ContextService';
import { useContextManager } from '../../hooks/useContextManager';
import { ContextItem, ItemType } from '../../domains/Context.domain';
import { DataClienteItem } from '../DataItems/DataClienteItem';
import { DataGestorItem } from '../DataItems/DataGestorItem';
import { DataPreevalItem } from '../DataItems/DataPreevalItem';
import { DataOperacionItem } from '../DataItems/DataOperacionItem';
import { DataIntervinienteItem } from '../DataItems/DataIntervinienteItem';
import { DataRecomendacionItem } from '../DataItems/DataRecomendacionItem';
import { DataMuestraInteresItem } from '../DataItems/DataMuestraInteresItem';
import { envVariables } from '../../config/env';

import {
  ContextPanelContainer,
  EmptySubtitle,
  EmptyTitle,
  EmptyState,
  Title,
  FooterContainer,
  Container,
  Label,
} from './ContextPanel.styled';

// mocks para pruebas
// import {
//   mockClienteItem,
//   mockGestorItem,
//   mockIntervinienteItem,
//   mockOperacionItem,
//   mockPreevalItem,
//   mockRecomendacionItem,
// } from './mockItems'; // Extrae los mocks a un archivo aparte si lo prefieres

function renderContextItem(item: ContextItem<ItemType>) {
  if (!item.itemType) {
    return (
      <div key={item.id} data-testid={item.id}>
        Tipo desconocido: {item.name}
      </div>
    );
  }

  switch (item.itemType) {
    case 'DataCliente':
      return (
        <AccordionTab key={item.id} header={item.name} data-test-id={item.id}>
          <DataClienteItem item={item} />
        </AccordionTab>
      );
    case 'DataGestor':
      return (
        <AccordionTab key={item.id} header="Datos del gestor" data-test-id={item.id}>
          <DataGestorItem item={item} />
        </AccordionTab>
      );
    case 'DataOperacion':
      return (
        <AccordionTab key={item.id} header={item.name} data-test-id={item.id}>
          <DataOperacionItem item={item} />
        </AccordionTab>
      );
    case 'DataInterviniente':
      return (
        <AccordionTab key={item.id} header={item.name} data-test-id={item.id}>
          <DataIntervinienteItem item={item} />
        </AccordionTab>
      );
    case 'DataPreeval':
      return (
        <AccordionTab key={item.id} header={item.name} data-test-id={item.id}>
          <DataPreevalItem item={item} />
        </AccordionTab>
      );
    case 'RecomendacionHipoteca':
      return (
        <AccordionTab key={item.id} header={item.name} data-test-id={item.id}>
          <DataRecomendacionItem item={item} />
        </AccordionTab>
      );
    case 'DataMuestraInteres':
      return (
        <AccordionTab key={item.id} header={item.name} data-test-id={item.id}>
          <DataMuestraInteresItem item={item} />
        </AccordionTab>
      );
    default:
      return (
        <div key={item.id} data-test-id={item.id}>
          Tipo desconocido: {item.name}
        </div>
      );
  }
}

type ContextPanelProps = {
  idSesion?: string; // opcional
};

export const ContextPanel: React.FC<ContextPanelProps> = ({ idSesion }) => {
  const [dialogVisible, setDialogVisible] = useState(false);
  const { items, setSesionItems } = useContextManager();
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileType, setFileType] = useState(null);
  const [pages, setPages] = useState('');

  const fileTypes = [
    { label: 'TIPO 1', value: 'TIPO_1' },
    { label: 'TIPO 2', value: 'TIPO_2' },
    { label: 'TIPO 3', value: 'TIPO_3' },
  ];

  useEffect(() => {
    if (idSesion) {
      // Obtener conversación
      getContextItems(idSesion);
    }
  }, [idSesion]);

  async function getContextItems(id: string) {
    const sesionItems = await contextService.getContextItems(id);
    setSesionItems(sesionItems);
  }

  const isEmpty = items.length === 0;

  const onUploadHandler = (event: any) => {
    if (event.files && event.files.length > 0) {
      setSelectedFile(event.files[0]);
    }
  };

  // Función para convertir "1-3,5" en [1,2,3,5]

  function parsePages(input: string): number[] {
    if (!input) {
      return [];
    }

    const result: number[] = [];
    const parts: string[] = input.split(',');

    parts.forEach((part: string) => {
      const trimmed = part.trim();
      if (trimmed.includes('-')) {
        const [startStr, endStr] = trimmed.split('-').map(s => s.trim());
        const start = Number(startStr);
        const end = Number(endStr);

        if (!Number.isNaN(start) && !Number.isNaN(end) && start <= end) {
          for (let i = start; i <= end; i++) {
            result.push(i);
          }
        }
        // Si el rango es inválido, puedes decidir ignorarlo o lanzar error.
      } else {
        const num = Number(trimmed);
        if (!Number.isNaN(num)) {
          result.push(num);
        }
      }
    });

    return result;
  }

  const handleSubmit = async () => {
    if (!selectedFile || !fileType) {
      setDialogVisible(false);
      return;
    }

    const pagesArray = parsePages(pages);

    const formData = new FormData();
    formData.append('fichero', selectedFile);
    formData.append('tipoFichero', fileType);
    formData.append('paginas', JSON.stringify(pagesArray));

    await fetch('/subirFichero', {
      method: 'POST',
      body: formData,
    });

    setDialogVisible(false);
  };

  const headerContent = <span>Adjuntar fichero</span>;

  const footerContent = (
    <FooterContainer>
      <Button label="Cancelar" onClick={() => setDialogVisible(false)} variant="secondary" />
      <Button label="Adjuntar fichero" onClick={handleSubmit} />
    </FooterContainer>
  );

  return (
    <ContextPanelContainer>
      <Dialog
        visible={dialogVisible}
        modal
        header={headerContent}
        footer={footerContent}
        style={{ width: '32rem' }}
        onHide={() => {
          if (!dialogVisible) return;
          setDialogVisible(false);
        }}>
        <Container>
          <p>Seleccione el fichero que desea adjuntar.</p>
          <FileUpload
            name="file"
            accept="application/pdf"
            maxFileSize={10000000}
            customUpload
            uploadHandler={onUploadHandler}
            chooseLabel="Seleccionar PDF"
            mode="basic"
          />
          <div>
            <Label htmlFor="fileType">Tipo de fichero</Label>
            <Dropdown
              value={fileType}
              options={fileTypes}
              onChange={(e: any) => setFileType(e.value)}
              placeholder="Seleccione un tipo"
            />
          </div>
          <div>
            <Label htmlFor="pages">Páginas a leer (ej: 1-3,5)</Label>
            <InputText value={pages} onChange={e => setPages(e.target.value)} placeholder="Ej: 1-3,5" />
          </div>
        </Container>
      </Dialog>

      {isEmpty ? (
        <EmptyState>
          <EmptyTitle>Panel de contexto</EmptyTitle>
          <EmptySubtitle>Aquí podrás consultar los datos más relevantes de tu conversación</EmptySubtitle>
        </EmptyState>
      ) : (
        <>
          <Title>
            <Icon name="computerDatabaseServer1" width={24} height={24} />
            <span>Panel de contexto</span>
            {typeof idSesion !== 'string' && envVariables.REACT_APP_SUBIR_FICHEROS && (
              <IconButton
                title="Subir fichero"
                variant="primary"
                icon={<Icon name="interfaceEditAttachment1" width={20} height={20} color="white"></Icon>}
                onClick={() => setDialogVisible(true)}></IconButton>
            )}
          </Title>
          <Accordion multiple>{items.map(renderContextItem)}</Accordion>
        </>
      )}
    </ContextPanelContainer>
  );
};

export default ContextPanel;
