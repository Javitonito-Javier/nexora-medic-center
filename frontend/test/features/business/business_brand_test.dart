import 'package:flutter_test/flutter_test.dart';
import 'package:clinicapharma_frontend/features/business/business_settings_api.dart';
import 'package:clinicapharma_frontend/features/business/widgets/business_brand.dart';

BusinessSettings _settings({String tradeName = '', String legalName = ''}) {
  return BusinessSettings(
    id: '1',
    tradeName: tradeName,
    legalName: legalName,
    rtn: '',
    address: '',
    phone: '',
    email: '',
    logoUrl: '',
    logoDataUrl: '',
    invoiceEnabled: false,
    fiscalEnabled: false,
    fiscalRegime: '',
    cai: '',
    invoiceRangeStart: '',
    invoiceRangeEnd: '',
    currentInvoiceNumber: '',
    establishmentCode: '',
    emissionPointCode: '',
    invoiceLimitDate: null,
    receiptFooter: '',
    invoiceFooter: '',
    ageDiscountNote: '',
    thermalPaperWidth: '80mm',
  );
}

void main() {
  group('businessDisplayName', () {
    test('returns fallback when settings is null', () {
      expect(businessDisplayName(null), 'Clinicapharma');
    });

    test('returns fallback when tradeName is empty or whitespace', () {
      expect(businessDisplayName(_settings(tradeName: '   ')), 'Clinicapharma');
    });

    test('returns trimmed tradeName when present', () {
      expect(businessDisplayName(_settings(tradeName: '  Mi Farmacia  ')),
          'Mi Farmacia');
    });
  });

  group('businessSubtitle', () {
    test('returns fallback when settings is null', () {
      expect(businessSubtitle(null), 'Clinica + farmacia');
    });

    test('returns fallback when legalName is empty or whitespace', () {
      expect(businessSubtitle(_settings(legalName: '  ')), 'Clinica + farmacia');
    });

    test('returns trimmed legalName when present', () {
      expect(businessSubtitle(_settings(legalName: '  Mi Razon Social  ')),
          'Mi Razon Social');
    });
  });
}
